# TODO: Update Workorder for update_pembayaran Field

## Tasks to Complete

- [ ] Update `schemas/service_workorder.py`:
  - Add `update_pembayaran: Optional[float] = None` to `CreateWorkOrder` schema.
  - Add `update_pembayaran: Optional[float] = None` to `CreateWorkorderOnly` schema.
  - Add `update_pembayaran: Optional[float] = None` to `WorkOrderResponse` schema.

- [ ] Update `services/services_workorder.py`:
  - In `createNewWorkorder` function, add assignment for `update_pembayaran` from `workorder_data`.
  - In `update_only_workorder` function, add assignment for `update_pembayaran` from `data`.
  - In `update_workorder_lengkap` function, add assignment for `update_pembayaran` from `data`.
  - Verify that `to_dict` function includes `update_pembayaran` (it should, as it iterates over columns).

## Followup Steps
- [ ] Verify that workorder creation and updates include the new field.
- [ ] Test the API endpoints to ensure no errors.
