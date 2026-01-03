"""
Permission reload router.

This module provides endpoints for reloading permissions from FastAPI routes.
"""

import csv
import io
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Response

from ..utils import ensure_acl_initialized
from ..dependency import policy_permission_required
from ..enforcer import acl

router = APIRouter(tags=["Casbin Policy"])


@router.get("/ptypes", name="casbin_policy_list_ptypes")
async def list_ptypes(
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    List all available policy types (ptypes) in the enforcer.

    Returns all ptypes that exist in the model, including p, g, g2, etc.

    :return: List of available ptypes
    """
    try:
        enforcer = acl.enforcer
        model = enforcer.model
        ptypes = []

        # Get all p types
        if "p" in model.model.keys():
            ptypes.extend(model.model["p"].keys())

        # Get all g types
        if "g" in model.model.keys():
            ptypes.extend(model.model["g"].keys())

        # Remove duplicates and sort
        ptypes = sorted(list(set(ptypes)))

        return {"ptypes": ptypes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list ptypes: {str(e)}")


@router.get("/export", name="casbin_policy_export")
async def export_policies(
    ptypes: str = Query(
        ..., description="policy type, multiple types separated by commas, e.g.: p,g,g2"
    ),
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    Export policy data as a CSV file.

    Supports exporting multiple policy types (e.g., p, g, g2).
    CSV format: ptype, v0, v1, v2, v3, v4, v5

    :param ptypes: policy type, multiple types separated by commas
    :return: CSV file response
    """
    try:
        # parse ptypes parameter
        ptype_list = [ptype.strip() for ptype in ptypes.split(",") if ptype.strip()]
        if not ptype_list:
            raise HTTPException(
                status_code=400, detail="At least one policy type is required"
            )

        enforcer = acl.enforcer
        model = enforcer.model
        all_policies = []

        # iterate over all requested ptypes
        for ptype in ptype_list:
            policies = []

            # handle p type policies
            if ptype == "p":
                policies = enforcer.get_policy()
            # handle g type policies (including g, g2, g3, etc.)
            elif ptype.startswith("g"):
                # try using get_named_grouping_policy
                try:
                    policies = enforcer.get_named_grouping_policy(ptype)
                except Exception:
                    # if failed, try to get from model directly
                    if "g" in model.model.keys():
                        if ptype in model.model["g"]:
                            policies = model.model["g"][ptype].policy
            # handle other named policy types (e.g., p2, p3, etc.)
            else:
                # try to get from model directly
                if "p" in model.model.keys():
                    if ptype in model.model["p"]:
                        policies = model.model["p"][ptype].policy

            # add policies to result list, each policy contains ptype
            for policy in policies:
                # fill policy values into 6 fields (v0-v5)
                policy_values = list(policy) + [None] * 6
                policy_values = policy_values[:6]
                all_policies.append([ptype] + policy_values)

        if not all_policies:
            raise HTTPException(
                status_code=404,
                detail=f"No policies found for type {ptypes}",
            )

        # create CSV content
        output = io.StringIO()
        writer = csv.writer(output)

        # write header
        writer.writerow(["ptype", "v0", "v1", "v2", "v3", "v4", "v5"])

        # write policy data
        for policy in all_policies:
            writer.writerow(policy)

        csv_content = output.getvalue()
        output.close()

        # return CSV file response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="casbin_policies_{ptypes.replace(",", "_")}.csv"'
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to export policies: {str(e)}"
        )


@router.post("/import", name="casbin_policy_import")
async def import_policies(
    file: UploadFile = File(
        ..., description="CSV file, format: ptype, v0, v1, v2, v3, v4, v5"
    ),
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    Incrementally import policy data from a CSV file.

    Incrementally import policy data from a CSV file into the enforcer. If the policy already exists, it will be skipped.
    After successful import, if Redis is configured, an update notification will be published.

    :param file: CSV file, format: ptype, v0, v1, v2, v3, v4, v5
    :return: import result statistics
    """
    try:
        # read file content
        content = await file.read()
        decoded_content = content.decode("utf-8")

        # parse CSV
        csv_reader = csv.reader(io.StringIO(decoded_content))

        # skip header
        header = next(csv_reader, None)
        if not header:
            raise HTTPException(
                status_code=400, detail="CSV file is empty or format is incorrect"
            )

        enforcer = acl.enforcer
        imported_count = 0
        skipped_count = 0
        error_count = 0
        errors = []

        # iterate over each row
        for row_num, row in enumerate(
            csv_reader, start=2
        ):  # start from the 2nd row (skip header)
            if not row or not any(row):  # skip empty rows
                continue

            try:
                # parse row data
                if len(row) < 1:
                    error_count += 1
                    errors.append(
                        f"Row {row_num}: data format is incorrect, missing ptype"
                    )
                    continue

                ptype = row[0].strip()
                if not ptype:
                    error_count += 1
                    errors.append(f"Row {row_num}: ptype cannot be empty")
                    continue

                # extract policy values (v0-v5), filter out None values
                policy_values = [v.strip() if v else None for v in row[1:7]]
                # remove trailing None values
                while policy_values and policy_values[-1] is None:
                    policy_values.pop()

                if not policy_values:
                    error_count += 1
                    errors.append(f"Row {row_num}: policy values cannot be empty")
                    continue

                # check if policy already exists
                exists = False
                if ptype == "p":
                    # for p type, use has_policy
                    exists = enforcer.has_policy(*policy_values)
                elif ptype.startswith("g"):
                    # for g type, use has_named_grouping_policy
                    try:
                        exists = enforcer.has_named_grouping_policy(
                            ptype, *policy_values
                        )
                    except Exception:
                        # if method does not exist, try to check from model
                        if "g" in enforcer.model.model.keys():
                            if ptype in enforcer.model.model["g"]:
                                existing_policies = enforcer.model.model["g"][
                                    ptype
                                ].policy
                                exists = list(policy_values) in existing_policies
                else:
                    # for other named policy types, check from model
                    if "p" in enforcer.model.model.keys():
                        if ptype in enforcer.model.model["p"]:
                            existing_policies = enforcer.model.model["p"][ptype].policy
                            exists = list(policy_values) in existing_policies

                if exists:
                    skipped_count += 1
                    continue

                # add policy
                added = False
                if ptype == "p":
                    added = await enforcer.add_policy(*policy_values)
                elif ptype.startswith("g"):
                    # for g type, use add_named_grouping_policy
                    try:
                        added = await enforcer.add_named_grouping_policy(
                            ptype, *policy_values
                        )
                    except AttributeError:
                        # if method does not exist, it means the ptype is not supported, skip
                        error_count += 1
                        errors.append(
                            f"Row {row_num}: unsupported policy type {ptype}, please use standard p or g type"
                        )
                        continue
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Row {row_num}: failed to add policy - {str(e)}")
                        continue
                else:
                    # for other named policy types (e.g., p2, p3), try to use add_named_policy
                    try:
                        added = await enforcer.add_named_policy(ptype, *policy_values)
                    except AttributeError:
                        # if method does not exist, it means the ptype is not supported, skip
                        error_count += 1
                        errors.append(
                            f"Row {row_num}: unsupported policy type {ptype}, please use standard p or g type"
                        )
                        continue
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Row {row_num}: failed to add policy - {str(e)}")
                        continue

                if added:
                    imported_count += 1
                else:
                    skipped_count += 1

            except Exception as e:
                error_count += 1
                errors.append(f"Row {row_num}: {str(e)}")

        # save policies to adapter
        if imported_count > 0:
            await acl.save_policy()

        # publish Redis update notification (if Redis is configured)
        await acl.notify_policy_update()

        # return import result
        result = {
            "imported": imported_count,
            "skipped": skipped_count,
            "errors": error_count,
            "message": f"Successfully imported {imported_count} policies, skipped {skipped_count} existing policies",
        }

        if errors:
            result["error_details"] = errors[:10]  # only return the first 10 errors
            if len(errors) > 10:
                result["error_details"].append(
                    f"... {len(errors) - 10} errors not displayed"
                )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to import policies: {str(e)}"
        )
