# EcoCode: AI-Powered Python Code Auditor for Energy Efficiency

## 🏆 Mastering the Kiro Platform

This project was built entirely using **Kiro's spec-driven development workflow**, demonstrating how AI-assisted development can produce high-quality, well-tested software with formal correctness guarantees.

### How We Used Kiro

#### 1. Spec-Driven Development
We leveraged Kiro's structured spec workflow to transform a rough idea into a complete implementation:

- **Requirements Phase**: Generated EARS-compliant requirements with INCOSE quality rules
- **Design Phase**: Created comprehensive design documents with architecture diagrams, component interfaces, and data models
- **Tasks Phase**: Broke down the design into incremental, actionable coding tasks

#### 2. Property-Based Testing Integration
Kiro guided us through formal correctness properties:

- **14 Correctness Properties** defined in the design document
- **21 Property-Based Tests** using Hypothesis library
- Each property validates specific requirements traceability

#### 3. Iterative Implementation
Using Kiro's task execution workflow:
- Tasks were implemented incrementally with checkpoints
- Each component was tested before integration
- Property tests caught edge cases that unit tests would miss

### Project Structure

```
.kiro/
├── hooks/
│   └── ecocode-green-audit.kiro.hook  # Auto-audit on file save
├── steering/
│   └── green-coding.md                # Green coding best practices
├── specs/
│   └── ecocode/
│       ├── requirements.md   # EARS-compliant requirements
│       ├── design.md         # Architecture & correctness properties
│       └── tasks.md          # Implementation checklist (all ✅)
src/
└── ecocode/
    ├── analysis.py           # Pattern detection (AST-based)
    ├── auditor.py            # Main orchestration
    ├── models.py             # Data models
    ├── refactoring.py        # Refactor plan generation
    ├── reporter.py           # JSON/Console output
    ├── scoring.py            # Green Score calculation
    └── watcher.py            # File monitoring
tests/
├── property/                 # Property-based tests (Hypothesis)
├── unit/                     # Unit tests
└── fixtures/                 # Sample code for testing
```

### Key Features Demonstrated

| Feature | Kiro Capability Used |
|---------|---------------------|
| Pattern Detection | Spec-driven design with AST analysis |
| Green Score | Property-based testing for score invariants |
| Refactoring Plans | Requirements traceability in tasks |
| JSON Serialization | Round-trip property testing |
| CLI Interface | Incremental task implementation |

### 🤖 Kiro Agent Integration

EcoCode is designed to be an agentic extension of the Kiro IDE:

- **Agent Hooks**: Includes a pre-configured `on_file_save` hook in the `.kiro/hooks/` folder. This triggers an automated audit every time a developer saves a Python file, delivering results directly to the Kiro Agent.

- **MCP Integration**: The Kiro Agent can utilize MCP servers when interpreting EcoCode's JSON reports. This allows the AI to provide real-world carbon and cost savings estimates during the refactoring conversation.

- **Steering Files**: Custom steering rules in `.kiro/steering/` guide the agent to prioritize energy efficiency suggestions and follow green coding best practices.

### Running the Project

```bash
# Install dependencies
pip install -e .

# Analyze a Python file
python -m ecocode --analyze your_file.py

# Output as JSON
python -m ecocode --analyze your_file.py --json

# Run all tests (21 property-based tests)
python -m pytest tests/ -v
```

### Correctness Properties Validated

1. **Python File Filtering** - Only .py files trigger analysis
2. **Issue Structure Completeness** - All issues have required fields
3. **Green Score Range Invariant** - Score always in [0, 100]
4. **Perfect Score for Clean Code** - Empty issues gives 100
5. **Score Determinism** - Same issues produce same score
6. **Severity Impact Ordering** - Higher severity = higher penalty
7. **Score Breakdown Consistency** - Penalties + score = 100
8. **RefactorPlan Completeness** - All plans have required fields
9. **RefactorPlan Priority Ordering** - Plans sorted by priority
10. **JSON Round-Trip Consistency** - Serialize/deserialize preserves data
11. **Nested Loop Detection** - Nested array loops are detected
12. **Redundant Computation Detection** - Loop-invariant code detected
13. **Model Loading in Loop Detection** - ML model loads in loops detected
14. **One RefactorPlan Per Issue** - Plan count equals issue count

### What Makes This Special

- **100% Test Pass Rate**: All 21 property-based tests pass
- **Formal Correctness**: Properties derived from EARS requirements
- **Full Traceability**: Every test maps to specific requirements
- **Clean Architecture**: Modular design following spec-driven patterns

---

*Built with Kiro - Where AI meets formal software engineering*
