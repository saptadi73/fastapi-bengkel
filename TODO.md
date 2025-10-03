# TODO: Fix UUID Error in Karyawan Routes

## Steps to Complete:
- [x] Reorder routes in routes/routes_karyawan.py: Move the /all route before the /{karyawan_id} route to prevent path matching conflict.
- [x] Add guard in get_karyawan_router: Check if karyawan_id == 'all' and return an error response indicating to use /all endpoint instead.
- [x] Fix get_all_karyawans function: Correct the to_dict call to handle list of objects instead of single object.
- [x] Test the changes: Verified fixes for both UUID error and list attribute error.
