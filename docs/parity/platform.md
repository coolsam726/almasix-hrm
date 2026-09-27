# Platform

- [x] Roles: administrator, supervisor, employee
- [x] A role grants read and write on a data group, with scope self, subordinates, or everyone
- [x] Subordinates include the whole reporting tree, not only direct reports
- [x] Turning a module off closes it, including for an administrator
- [x] Workflow rows are `(flow, state, role, action) -> next state`
- [x] A role without a matching row cannot take the action
- [x] A successful transition notifies the employee
- [x] Sample company: Ada, Grace, and Alan
