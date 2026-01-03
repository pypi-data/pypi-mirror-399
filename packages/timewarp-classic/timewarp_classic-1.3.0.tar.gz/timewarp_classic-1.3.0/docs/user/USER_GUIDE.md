# Time Warp Classic - Complete User Guide

Master all features of the Time Warp multi-language IDE.

## Table of Contents

1. [IDE Overview](#ide-overview)
2. [Editor Features](#editor-features)
3. [Running Programs](#running-programs)
4. [File Operations](#file-operations)
5. [Debugging & Output](#debugging--output)
6. [Customization](#customization)
7. [Advanced Features](#advanced-features)
8. [Best Practices](#best-practices)
9. [Tips & Tricks](#tips--tricks)

---

## IDE Overview

### Main Window Layout

```
┌─────────────────────────────────────────────────┐
│ File Edit Program Debug Test Performance Help   │ ← Menu Bar
├──────────┬──────────────────────────┬──────────┤
│          │                          │          │
│ Language │      Editor Panel        │ Turtle   │
│ Selector │   (Write Code Here)      │ Canvas   │
│          │                          │          │
│ ▼ PYTHON │                          │ (Logo)   │
├──────────┼──────────────────────────┼──────────┤
│ Input    │                          │          │
├──────────┤   Output Panel           │          │
│ Run Btn  │   (Program Results)      │          │
└──────────┴──────────────────────────┴──────────┘
```

### Key Areas

**Language Selector**
- Dropdown at top-left
- Choose from 9 languages
- Changes syntax highlighting

**Editor Panel (Left)**
- Write your program
- Automatic syntax highlighting
- Line numbers
- Smart indentation

**Output Panel (Bottom)**
- Program output appears here
- Error messages displayed
- Performance metrics (if enabled)

**Turtle Canvas (Right)**
- Visual output for Logo programs
- Graphics rendering
- Zoom and pan controls

**Toolbar**
- Run button (execute program)
- File operations
- Settings access

---

## Editor Features

### Basic Editing

**Create New Program**
- File → New
- Or start typing directly

**Open Existing File**
- File → Open File
- Select .bas, .py, .js, .pas, .pl, .fth, .logo, .pilot file
- Code loads into editor

**Syntax Highlighting**
- Automatic for each language
- Color-coded keywords, strings, comments
- Helps identify errors

**Line Numbers**
- Click number to jump to line
- Shows code position

### Text Selection & Editing

**Select All**
- Ctrl+A or Edit → Select All
- Selects entire program

**Copy/Paste**
- Ctrl+C: Copy selected text
- Ctrl+V: Paste
- Ctrl+X: Cut

**Undo/Redo**
- Ctrl+Z: Undo last change
- Ctrl+Y: Redo

### Find & Replace

**Find Text**
- Ctrl+F: Open Find dialog
- Enter search term
- Highlights all matches
- Use arrows to navigate

**Find & Replace**
- Ctrl+H: Open Find & Replace
- Enter find text
- Enter replacement text
- Replace one or all occurrences

**Case Sensitivity**
- Option to match case
- Helpful for variable names

### Code Navigation

**Go to Line**
- Ctrl+G: Open Go to Line dialog
- Enter line number
- Jumps to that line

**Jump to Definition**
- Click on variable/function name
- Ctrl+Click to navigate

**Auto-Indentation**
- Tab: Indent line
- Shift+Tab: Unindent
- Automatic for blocks

---

## Running Programs

### Basic Execution

**Run Current Program**
- Click "Run" button
- Or press Ctrl+Enter
- Output appears immediately

**Stop Execution**
- Click "Stop" (if available)
- Stops running program

**Clear Output**
- Output → Clear
- Clears previous output

### Language Selection

**Change Language**
- Click language dropdown
- Select from 9 languages:
  - BASIC
  - Python
  - JavaScript
  - Pascal
  - Prolog
  - Forth
  - Perl
  - Logo
  - PILOT

**Important:** Language must match your code!

### Program Input

**For Programs Expecting Input**
- Input field above Run button
- Type your input
- Press Enter when program requests it
- Input passed to program

### Execution Modes

**Normal Mode**
- Standard program execution
- All output to Output panel
- Interactive input supported

**Debug Mode**
- Step through code line-by-line
- Monitor variables
- Check execution flow

---

## File Operations

### Save Your Work

**Save Current File**
- Ctrl+S or File → Save
- Choose location and name
- Must choose correct extension:
  - .bas (BASIC)
  - .py (Python)
  - .js (JavaScript)
  - .pas (Pascal)
  - .pl (Prolog/Perl)
  - .fth (Forth)
  - .logo (Logo)
  - .pilot (PILOT)

**Save As**
- File → Save As
- Save with different name/location

### Open & Load

**Open File**
- File → Open File
- Browse for file
- Select and open
- Code loads into editor

**Recent Files**
- File → Recent Files
- Quick access to recently opened files

**Load Example**
- File → Examples
- Browse example programs
- Load directly into editor

### File Management

**New File**
- File → New
- Clear editor, ready for new code

**File Info**
- File → Properties
- Shows file details
- Location, size, modification date

---

## Debugging & Output

### Output Panel

**Program Output**
- Standard print/output statements appear
- Formatted with proper line breaks
- Scrollable if long output

**Error Messages**
- Syntax errors highlighted
- Runtime errors with line numbers
- Clear description of problem

**Section Headers**
- Demos use section headers
- Helps follow program flow
- Shows feature demonstrations

### Debugging Features

**Debug Mode**
- Step through code
- Watch variables change
- Breakpoints (where supported)

**Variable Inspector**
- View variable values
- Track during execution
- Helpful for learning

**Performance Monitor**
- Execution time displayed
- Memory usage (if available)
- Performance optimization tips

### Common Output Issues

| Problem | Solution |
|---------|----------|
| No output | Check PRINT statements are used |
| Output cut off | Scroll down in Output panel |
| Error message | Read error carefully, check line number |
| Slow execution | Some languages (Prolog) are intentionally slower |

---

## Customization

### Themes

**Available Themes**
- Light (white background)
- Dark (black background)
- High Contrast (for accessibility)
- Solarized (popular editor theme)
- Dracula
- Monokai
- And more!

**Change Theme**
- Edit → Preferences → Appearance
- Select theme from list
- Applies immediately

### Font Settings

**Font Size**
- 7 sizes available
- Edit → Preferences → Font
- Choose comfortable reading size
- Applies to editor only

**Font Family**
- Monospace fonts recommended
- Common choices:
  - Courier New
  - Consolas
  - Monaco
  - Ubuntu Mono

### Editor Preferences

**Line Numbers**
- Toggle on/off
- Preferences → Editor → Show Line Numbers

**Word Wrap**
- Enable for long lines
- Preferences → Editor → Word Wrap

**Tab Size**
- Set indentation width
- Preferences → Editor → Tab Size (typically 4)

**Auto-Save**
- Enable automatic saving
- Preferences → Editor → Auto-Save

---

## Advanced Features

### Multi-File Programs

**Limited Support**
- Most languages have single-file programs
- Some support include/import:
  - Prolog: consult/1
  - Perl: use/require
  - Python: import (limited)

### Graphics Output (Logo)

**Turtle Canvas**
- Right panel shows graphics
- Commands:
  - FORWARD/FD: Move forward
  - RIGHT/RT: Turn right
  - PENUP/PU: Lift pen
  - PENDOWN/PD: Lower pen
  - SETPENCOLOR: Change color

**Canvas Controls**
- Zoom in/out with mouse wheel
- Pan by dragging
- Clear canvas with CLEARSCREEN
- Reset with HOME

### Performance Analysis

**Enable Performance Monitoring**
- Preferences → Performance
- Shows execution time
- Displays metrics after run

**Optimize Programs**
- Check execution time
- Identify slow sections
- Use built-in functions (faster than loops)

---

## Best Practices

### Code Organization

**Write Clear Comments**
```
REM This is a BASIC comment
// This is a JavaScript comment
# This is a Python comment
```

**Use Meaningful Names**
- Variables: age, total_sum, user_name
- Functions: calculate_factorial, print_menu
- Avoid: x, y, z (unless mathematical)

**Proper Indentation**
- Use consistent indentation
- 4 spaces per level
- Makes code readable

### Debugging Tips

**Start Simple**
- Write small pieces first
- Test each part separately
- Build up complexity

**Use Print Statements**
- Output variable values
- Trace program flow
- Verify assumptions

**Read Error Messages**
- Usually very clear
- Include line number
- Indicate the problem

### Performance Tips

**Avoid Infinite Loops**
- Always have exit condition
- Test with small inputs first
- Use timeout if needed

**Use Efficient Algorithms**
- Built-in functions are faster
- Avoid nested loops when possible
- Consider algorithm complexity

---

## Tips & Tricks

### Keyboard Shortcuts

```
Ctrl+A         Select All
Ctrl+C         Copy
Ctrl+X         Cut
Ctrl+V         Paste
Ctrl+Z         Undo
Ctrl+Y         Redo
Ctrl+F         Find
Ctrl+H         Find & Replace
Ctrl+S         Save
Ctrl+O         Open
Ctrl+Enter     Run Program
Ctrl+G         Go to Line
```

### Quick Commands

**Run Examples Quickly**
- Open examples from File menu
- Select language first
- Code loads and ready to run

**Compare Languages**
- Keep similar programs in two windows
- Switch language dropdown
- See syntax differences

**Test Incrementally**
- Write a few lines
- Run to test
- Add more lines
- Test again

### Common Patterns

**Loop N Times (BASIC)**
```basic
FOR i = 1 TO 10
    PRINT i
NEXT i
```

**Loop N Times (Python)**
```python
for i in range(1, 11):
    print(i)
```

**Conditional (All Languages)**
```
Check condition → Execute if true → Skip if false
```

### Productivity Hacks

**Copy from Examples**
- Open example file
- Ctrl+A to select all
- Ctrl+C to copy
- Ctrl+V to paste into editor

**Save Templates**
- Create template programs
- Save with meaningful names
- Load when starting new project

**Use Auto-Save**
- Enable auto-save feature
- Never lose your work
- Save happens silently

---

## Troubleshooting

### Program Won't Run

**Issue:** "Unknown language selected"
**Solution:** Make sure language dropdown matches code type

**Issue:** Syntax error
**Solution:** Check line indicated in error message

**Issue:** No output
**Solution:** Verify program has PRINT/output statements

### Graphics Not Showing (Logo)

**Issue:** Canvas is blank
**Solution:**
- Make sure PENDOWN is called
- Verify FORWARD commands move pen
- Check SETPENCOLOR sets visible color

### Performance Issues

**Issue:** Program runs slowly
**Solution:**
- Some languages (Prolog) intentionally slower
- Check for infinite loops
- Optimize algorithms

---

## Next Steps

- **Learn specific language:** [LANGUAGE_TUTORIALS.md](LANGUAGE_TUTORIALS.md)
- **Language reference:** [../languages/](../languages/) directory
- **More examples:** [../../examples/](../../examples/)
- **Troubleshooting:** [../TROUBLESHOOTING.md](../TROUBLESHOOTING.md)

---

**Happy Coding! 🚀**

Master all features of Time Warp Classic and become a programming polyglot!
