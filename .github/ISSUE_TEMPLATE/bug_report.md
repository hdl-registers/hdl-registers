---
name: Bug report
about: Create a report to help us improve
title: ''
labels: Bug
assignees: ''

---

**Description**
A clear and concise description of what the issue is about.


**Expected behavior**
What you expected to happen, and what is happening instead.


**How to reproduce?**
Tell us how to reproduce this issue.
Please provide a Minimal Working Example (MWE) that triggers the issue.
With sample code it's easier to reproduce and much faster to fix.

Add code for example like this:

```toml
[register.config]

mode = "w"

integer.increment.max_value = 100
```

```vhdl
architecture a of ent_name is
  signal slv : std_ulogic_vector(6 downto 0) := (others => '0');
begin
  slv <= to_slv(regs_down.config.increment);
end architecture;
```


**Context**
Please provide the following information:

- Operating system: [e.g. Ubuntu 22.04]
- Python version: [e.g. 3.11]
- hdl-registers origin:
  - [ ] Released package.
  - [ ] Git repository.
- hdl-registers version: [e.g. 4.1.0, or git commit SHA]
- Any other relevant tool version(s):
  - [e.g. compiler, FPGA build tool, simulator, etc.]


**Additional context**
Add any other context about the problem here.
If applicable, add screenshots to help explain your problem.
