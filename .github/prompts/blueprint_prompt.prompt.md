---
agent: agent
---
## Context:
Project: A Python visual programming tool based on PySide6, specifically designed for game MOD creation.
Application Scenario: Game MOD creation, where users generate MOD scripts through visual node programming.
Development Mode: AI handles technical implementation, users provide requirement feedback and resource files.
Technology Stack: Python 3.13, PySide6 (Qt for Python), Unreal Blueprint-like interface style.
Implementation Requirements:
1. Modular development, ultimately consolidated into a complete Pull Request
2. A complete project directory tree structure must be provided
3. The project modifies an existing codebase and requires frequent refactoring
4. Manage game resources: including localized text, image icons, MOD script code, etc.

## Objective:
Core Functional Modules:
1. Visual Programming Interface: Unreal Blueprint-like node editing experience supporting drag-and-drop connections
2. Custom Node System: Users can create, edit, and save custom function nodes
3. Code Generation Engine: Convert node graphs into executable MOD scripts
4. Real-time Preview System: Display MOD effect preview in real-time during editing
5. Resource Management System: Manage localized text files, image icon resources, and generated MOD scripts
6. Test Suite: Provide unit tests and integration tests for key functional modules

Specific Technical Requirements:
- Bidirectional synchronization between node graphs and code
- Support for node grouping and subgraph functionality
- Built-in nodes for common game APIs
- Resource file version management and import/export functionality
- Comprehensive error handling and user-friendly prompts

## Style:
Code Standards:
- Strictly adhere to PEP 8 coding standards
- Use type annotations (Python 3.8+ Type Hints)
- Detailed Google-style docstrings

Naming Conventions:
- Class names: CamelCase (e.g., NodeEditor, ResourceManager)
- Function names: CamelCase (e.g., CreateNode, GenerateCode)
- Variable names: snake_case (e.g., node_graph, selected_nodes)
- Constant names: UPPER_CASE (e.g., MAX_NODES, DEFAULT_THEME)

Architecture Design:
- Modular design with high cohesion and low coupling between functional components
- Facilitates subsequent AI maintenance and modifications
- Clear interface definitions and dependency management

UI Design:
- Dark theme: References UE5 design language, professional game development style
- Light theme: Modern software interface, clean and clear
- Responsive layout supporting different resolutions

## Tone:
Technical Implementation Parts:
- Professional and pragmatic with strong technical focus
- Code and documentation maintain technical accuracy
- Architectural design decisions accompanied by technical rationale

Product Design Parts:
- Collaborative guidance style, explaining design thinking
- User interaction design considering ease of use
- Friendly and clear error prompts and help information

Mixed Strategy:
- Technical documentation: Professional and rigorous
- User manual: Friendly and easy to understand
- Code comments: Practical and direct

## Audience:
Primary User Group:
- Programming level: Beginners, only capable of using simple visual software
- Technical background: No programming experience required, can draw simple flowcharts
- Usage scenario: Game MOD creation, particularly simplifying complex MOD development through visual methods
- Core need: Complete complex MOD logic writing through simple node dragging
- Pain point: Traditional MOD development requires programming knowledge, aiming to lower the barrier

## Response:
Deliverable Requirements:
1. User Manual in Chinese (for beginners)
   - Illustrated getting started guide
   - Step-by-step operation tutorials
   - Frequently asked questions
   - Practical MOD creation cases throughout

2. API Documentation (for AI query only)
   - Complete module API reference
   - Detailed class and method explanations
   - Internal architecture and design pattern documentation
   - Extension development guide

Project Delivery:
- Complete runnable project code
- Developed modularly, ultimately integrated and submitted
- Includes all dependency configurations and running instructions
