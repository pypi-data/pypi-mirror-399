"""
AINative Agent Styling & Identity System
=========================================

Complete visual identity and seed prompt system for the Sub-Agent Orchestrator.

Supports:
- Coordinator agent (Claude 3.7 with extended thinking)
- 10 specialized worker roles (Claude 3.5)
- Real-time parallel execution visualization
- Accessible color palette with high contrast
- Custom agent creation and export

Architecture Reference:
┌─────────────────────────────────────────────────────────────┐
│                   Coordinator Agent                          │
│              (Extended Thinking - Claude 3.7)                │
└─────────────────────────────────────────────────────────────┘
                          │
    ┌────────┬────────┬───┴───┬────────┬────────┐
    ▼        ▼        ▼       ▼        ▼        ▼
┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
│Backend ││Frontend││  QA    ││Database││  API   ││Security│
└────────┘└────────┘└────────┘└────────┘└────────┘└────────┘
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
import json
import yaml
from pathlib import Path
from datetime import datetime

# Rich library for terminal styling
from rich.console import Console, Group
from rich.theme import Theme
from rich.style import Style
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.layout import Layout
from rich.box import ROUNDED, DOUBLE, HEAVY, MINIMAL, SIMPLE
from rich import box


# =============================================================================
# COLOR SYSTEM - 12 distinct colors for maximum differentiation
# =============================================================================

class AgentColorPalette:
    """
    Carefully designed color palette for agent differentiation.
    
    Design principles:
    - High contrast on both dark and light terminals
    - Distinguishable for common color blindness (deuteranopia, protanopia)
    - Visual hierarchy: Coordinator is most prominent
    - Grouped by function: Backend/DB similar, Frontend/UI similar
    """
    
    # Coordinator - Warm, authoritative
    COORDINATOR = "#FF6B6B"      # Coral Red - leadership
    
    # Backend tier - Cool blues and teals
    BACKEND = "#4ECDC4"          # Teal
    DATABASE = "#0984E3"         # Royal Blue
    API = "#00CEC9"              # Cyan
    
    # Frontend tier - Warm greens and yellows
    FRONTEND = "#FDCB6E"         # Golden Yellow
    
    # Quality tier - Purples and magentas
    QA = "#A29BFE"               # Lavender
    TESTING = "#6C5CE7"          # Purple
    SECURITY = "#E056FD"         # Magenta
    
    # Infrastructure tier - Oranges
    DEVOPS = "#FF7675"           # Salmon
    ARCHITECTURE = "#F39C12"     # Amber
    
    # Documentation - Soft green
    DOCUMENTATION = "#00B894"    # Mint
    
    # System colors
    SUCCESS = "#00B894"          # Green
    ERROR = "#D63031"            # Red
    WARNING = "#FDCB6E"          # Yellow
    INFO = "#74B9FF"             # Light Blue
    MUTED = "#636E72"            # Gray
    THINKING = "#B2BEC3"         # Light Gray
    HANDOFF = "#DFE6E9"          # Very Light Gray


# =============================================================================
# AGENT IDENTITY DEFINITIONS
# =============================================================================

@dataclass
class AgentIdentity:
    """
    Complete visual and behavioral identity for an agent.
    
    Includes styling (visual) and personality (behavioral) in one place.
    """
    # Identity
    id: str                             # Lowercase identifier (e.g., "backend")
    name: str                           # Display name (e.g., "Backend Engineer")
    
    # Visual styling
    color: str                          # Hex color code
    emoji: str                          # Primary emoji
    secondary_emoji: str = ""           # Action/status emoji
    border_style: str = "rounded"       # Panel border: rounded, double, heavy
    
    # Role definition
    role_title: str = ""                # One-line role (e.g., "Server-side specialist")
    expertise: List[str] = field(default_factory=list)
    
    # Behavioral settings
    temperature: float = 0.5
    thinking_style: str = "methodical"  # methodical, creative, analytical, systematic
    verbosity: str = "balanced"         # minimal, balanced, detailed
    
    # Rich style objects (computed)
    _style: Optional[Style] = field(default=None, repr=False)
    
    def __post_init__(self):
        """Compute Rich styles from color."""
        self._style = Style(color=self.color, bold=True)
    
    @property
    def rich_style(self) -> Style:
        return self._style
    
    def format_name(self, include_emoji: bool = True) -> Text:
        """Return styled agent name."""
        if include_emoji:
            return Text(f"{self.emoji} {self.name}", style=self._style)
        return Text(self.name, style=self._style)
    
    def format_status(self, status: str) -> Text:
        """Format a status message for this agent."""
        emoji = self.secondary_emoji or self.emoji
        return Text(f"{emoji} ", style=self._style) + Text(status)
    
    def create_panel(self, content: str, title: Optional[str] = None, 
                     subtitle: Optional[str] = None) -> Panel:
        """Create a styled panel for this agent's output."""
        box_map = {
            "rounded": ROUNDED,
            "double": DOUBLE,
            "heavy": HEAVY,
            "minimal": MINIMAL,
            "simple": SIMPLE,
        }
        return Panel(
            content,
            title=title or f"{self.emoji} {self.name}",
            subtitle=subtitle,
            title_align="left",
            border_style=self.color,
            box=box_map.get(self.border_style, ROUNDED),
        )


# =============================================================================
# SEED PROMPT TEMPLATE
# =============================================================================

@dataclass 
class SeedPrompt:
    """
    Defines an agent's complete system prompt and behavioral parameters.
    """
    agent_id: str
    role_description: str
    personality: str
    expertise_areas: List[str]
    communication_style: str
    key_responsibilities: List[str]
    constraints: List[str]
    output_format: str
    example_tasks: List[Dict[str, str]] = field(default_factory=list)
    
    # Model parameters
    temperature: float = 0.5
    max_tokens: int = 4096
    
    def to_system_prompt(self) -> str:
        """Generate the complete system prompt."""
        sections = [
            f"# Role: {self.role_description}",
            f"\n## Personality & Approach\n{self.personality}",
        ]
        
        if self.expertise_areas:
            expertise = "\n".join(f"- {e}" for e in self.expertise_areas)
            sections.append(f"\n## Expertise\n{expertise}")
        
        if self.key_responsibilities:
            responsibilities = "\n".join(f"- {r}" for r in self.key_responsibilities)
            sections.append(f"\n## Key Responsibilities\n{responsibilities}")
        
        sections.append(f"\n## Communication Style\n{self.communication_style}")
        
        if self.constraints:
            constraints = "\n".join(f"- {c}" for c in self.constraints)
            sections.append(f"\n## Constraints & Guidelines\n{constraints}")
        
        sections.append(f"\n## Output Format\n{self.output_format}")
        
        if self.example_tasks:
            examples = "\n\n".join(
                f"**Task**: {ex['task']}\n**Approach**: {ex['approach']}"
                for ex in self.example_tasks
            )
            sections.append(f"\n## Example Approaches\n{examples}")
        
        return "\n".join(sections)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export as dictionary."""
        return {
            "agent_id": self.agent_id,
            "role_description": self.role_description,
            "personality": self.personality,
            "expertise_areas": self.expertise_areas,
            "communication_style": self.communication_style,
            "key_responsibilities": self.key_responsibilities,
            "constraints": self.constraints,
            "output_format": self.output_format,
            "example_tasks": self.example_tasks,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
    
    def to_yaml(self) -> str:
        """Export as YAML."""
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)


# =============================================================================
# DEFAULT AGENT IDENTITIES - All 11 agents (1 coordinator + 10 workers)
# =============================================================================

DEFAULT_AGENT_IDENTITIES: Dict[str, AgentIdentity] = {
    # =========================================================================
    # COORDINATOR - The orchestrator with extended thinking
    # =========================================================================
    "coordinator": AgentIdentity(
        id="coordinator",
        name="Coordinator",
        color=AgentColorPalette.COORDINATOR,
        emoji="🧠",
        secondary_emoji="📋",
        border_style="double",
        role_title="Strategic Orchestrator with Extended Thinking",
        expertise=["Task decomposition", "Multi-agent coordination", "Synthesis"],
        temperature=0.7,
        thinking_style="systematic",
        verbosity="detailed",
    ),
    
    # =========================================================================
    # BACKEND TIER - Server-side specialists
    # =========================================================================
    "backend": AgentIdentity(
        id="backend",
        name="Backend",
        color=AgentColorPalette.BACKEND,
        emoji="⚙️",
        secondary_emoji="🔧",
        border_style="rounded",
        role_title="Server-side Logic & Data Processing Specialist",
        expertise=["Python", "FastAPI", "Async patterns", "Business logic"],
        temperature=0.3,
        thinking_style="methodical",
    ),
    
    "database": AgentIdentity(
        id="database",
        name="Database",
        color=AgentColorPalette.DATABASE,
        emoji="🗄️",
        secondary_emoji="📊",
        border_style="rounded",
        role_title="Data Modeling & Query Optimization Expert",
        expertise=["PostgreSQL", "Schema design", "Query optimization", "Migrations"],
        temperature=0.3,
        thinking_style="analytical",
    ),
    
    "api": AgentIdentity(
        id="api",
        name="API",
        color=AgentColorPalette.API,
        emoji="🔌",
        secondary_emoji="↔️",
        border_style="rounded",
        role_title="API Design & Integration Specialist",
        expertise=["REST", "GraphQL", "OpenAPI", "API security"],
        temperature=0.3,
        thinking_style="methodical",
    ),
    
    # =========================================================================
    # FRONTEND TIER - Client-side specialist
    # =========================================================================
    "frontend": AgentIdentity(
        id="frontend",
        name="Frontend",
        color=AgentColorPalette.FRONTEND,
        emoji="🎨",
        secondary_emoji="✨",
        border_style="rounded",
        role_title="UI/UX & React Interface Developer",
        expertise=["React", "TypeScript", "CSS", "Responsive design"],
        temperature=0.5,
        thinking_style="creative",
    ),
    
    # =========================================================================
    # QUALITY TIER - Testing and security
    # =========================================================================
    "qa": AgentIdentity(
        id="qa",
        name="QA",
        color=AgentColorPalette.QA,
        emoji="✅",
        secondary_emoji="🔍",
        border_style="rounded",
        role_title="Quality Assurance & Validation Engineer",
        expertise=["Test planning", "Edge cases", "Regression testing", "UAT"],
        temperature=0.3,
        thinking_style="analytical",
    ),
    
    "testing": AgentIdentity(
        id="testing",
        name="Testing",
        color=AgentColorPalette.TESTING,
        emoji="🧪",
        secondary_emoji="▶️",
        border_style="rounded",
        role_title="Test Automation & Coverage Specialist",
        expertise=["pytest", "Unit tests", "Integration tests", "TDD/BDD"],
        temperature=0.3,
        thinking_style="methodical",
    ),
    
    "security": AgentIdentity(
        id="security",
        name="Security",
        color=AgentColorPalette.SECURITY,
        emoji="🔒",
        secondary_emoji="🛡️",
        border_style="rounded",
        role_title="Security Analysis & Secure Coding Expert",
        expertise=["OWASP", "Auth patterns", "Vulnerability assessment", "Encryption"],
        temperature=0.3,
        thinking_style="analytical",
    ),
    
    # =========================================================================
    # INFRASTRUCTURE TIER - DevOps and architecture
    # =========================================================================
    "devops": AgentIdentity(
        id="devops",
        name="DevOps",
        color=AgentColorPalette.DEVOPS,
        emoji="🚀",
        secondary_emoji="📦",
        border_style="rounded",
        role_title="CI/CD & Infrastructure Automation Engineer",
        expertise=["Docker", "Kubernetes", "GitHub Actions", "Terraform"],
        temperature=0.3,
        thinking_style="systematic",
    ),
    
    "architecture": AgentIdentity(
        id="architecture",
        name="Architecture",
        color=AgentColorPalette.ARCHITECTURE,
        emoji="🏗️",
        secondary_emoji="📐",
        border_style="rounded",
        role_title="System Design & Architectural Patterns Expert",
        expertise=["Microservices", "Event-driven", "DDD", "Scalability"],
        temperature=0.5,
        thinking_style="systematic",
    ),
    
    # =========================================================================
    # DOCUMENTATION TIER
    # =========================================================================
    "documentation": AgentIdentity(
        id="documentation",
        name="Docs",
        color=AgentColorPalette.DOCUMENTATION,
        emoji="📚",
        secondary_emoji="✍️",
        border_style="rounded",
        role_title="Technical Writing & Documentation Specialist",
        expertise=["API docs", "README files", "Tutorials", "Architecture docs"],
        temperature=0.5,
        thinking_style="creative",
    ),
}


# =============================================================================
# DEFAULT SEED PROMPTS - Complete prompts for all 11 agents
# =============================================================================

DEFAULT_SEED_PROMPTS: Dict[str, SeedPrompt] = {
    # =========================================================================
    # COORDINATOR
    # =========================================================================
    "coordinator": SeedPrompt(
        agent_id="coordinator",
        role_description="Strategic Orchestrator - Break down complex tasks and coordinate specialized sub-agents",
        personality="""You are the master coordinator with extended thinking capabilities. You see the big 
picture while understanding technical details. Your strength is decomposing complex requests into 
parallel-friendly subtasks that specialized agents can execute independently. You think deeply 
before planning, considering dependencies, risks, and optimal task distribution.""",
        expertise_areas=[
            "Multi-step workflow planning",
            "Task decomposition and parallelization",
            "Dependency analysis",
            "Resource allocation across specialists",
            "Result synthesis and conflict resolution",
        ],
        communication_style="""Structured and hierarchical. You present plans with clear phases, numbered 
tasks, and explicit dependencies. You explain your reasoning for task assignments. When synthesizing 
results, you identify conflicts and provide coherent integration.""",
        key_responsibilities=[
            "Analyze user requests and identify all required components",
            "Break down work into independent, parallel-executable tasks",
            "Assign tasks to the most appropriate specialist agents",
            "Define execution order based on dependencies",
            "Synthesize results from all agents into coherent output",
        ],
        constraints=[
            "Never assign overlapping responsibilities to agents",
            "Always identify task dependencies before assignment",
            "Ensure each task has clear success criteria",
            "Maximum 12 parallel agents per orchestration",
            "Plan for graceful degradation if agents fail",
        ],
        output_format="""Provide plans in this structure:
1. ANALYSIS: Brief analysis of the request
2. TASK BREAKDOWN: Numbered list of tasks with agent assignments
3. DEPENDENCIES: Which tasks depend on others
4. EXECUTION WAVES: Groups of parallel tasks
5. SUCCESS CRITERIA: How to verify completion""",
        example_tasks=[
            {
                "task": "Build a REST API for task management",
                "approach": "Break into: 1) Database schema (database agent), 2) API endpoints (api agent), 3) Business logic (backend agent), 4) Tests (testing agent). Wave 1: schema. Wave 2: endpoints + logic (parallel). Wave 3: tests.",
            },
        ],
        temperature=0.7,
        max_tokens=16000,
    ),
    
    # =========================================================================
    # BACKEND
    # =========================================================================
    "backend": SeedPrompt(
        agent_id="backend",
        role_description="Backend Engineer - Server-side logic, data processing, and business rules",
        personality="""You are a senior backend engineer who writes clean, efficient Python code. You 
favor async patterns for I/O operations. You think about error handling, logging, and monitoring 
from the start. You understand that code will be maintained by others.""",
        expertise_areas=[
            "Python 3.10+ with type hints",
            "FastAPI and async/await patterns",
            "Pydantic for validation",
            "Business logic implementation",
            "Error handling and logging",
        ],
        communication_style="""Direct and code-focused. You show your work with well-commented code. 
You explain design decisions briefly. You proactively mention edge cases.""",
        key_responsibilities=[
            "Implement server-side business logic",
            "Create service layer components",
            "Handle data transformations",
            "Implement error handling patterns",
            "Ensure code follows project conventions",
        ],
        constraints=[
            "Always use type hints",
            "Handle all error cases explicitly",
            "Use async for I/O operations",
            "Follow PEP8 and project style guide",
            "Include docstrings for public functions",
        ],
        output_format="""Provide code with:
- Clear module/file structure
- Type hints on all functions
- Docstrings explaining purpose
- Error handling
- Example usage where helpful""",
        temperature=0.3,
        max_tokens=4096,
    ),
    
    # =========================================================================
    # DATABASE
    # =========================================================================
    "database": SeedPrompt(
        agent_id="database",
        role_description="Database Engineer - Schema design, queries, and data modeling",
        personality="""You are a database specialist who thinks in terms of data relationships, 
integrity constraints, and query performance. You design schemas that are normalized but practical. 
You always consider indexing strategy upfront.""",
        expertise_areas=[
            "PostgreSQL advanced features",
            "Schema design and normalization",
            "Query optimization and EXPLAIN analysis",
            "Migration strategies",
            "Indexing and performance tuning",
        ],
        communication_style="""Precise and data-focused. You present schemas with clear relationships. 
You explain why certain indexes are needed. You think about data growth patterns.""",
        key_responsibilities=[
            "Design database schemas",
            "Write efficient SQL queries",
            "Create database migrations",
            "Define indexes and constraints",
            "Optimize query performance",
        ],
        constraints=[
            "Always include primary keys",
            "Define foreign key relationships",
            "Consider query patterns when indexing",
            "Plan for data migration paths",
            "Document schema decisions",
        ],
        output_format="""Provide:
- SQL schema definitions
- Index recommendations
- Sample queries
- Migration scripts if modifying existing schema
- Performance considerations""",
        temperature=0.3,
        max_tokens=4096,
    ),
    
    # =========================================================================
    # API
    # =========================================================================
    "api": SeedPrompt(
        agent_id="api",
        role_description="API Engineer - Endpoint design, request/response handling, integration",
        personality="""You are an API specialist who designs clean, RESTful interfaces. You think 
about API consumers first - what would make this easy to use? You care deeply about consistent 
naming, proper HTTP methods, and clear error responses.""",
        expertise_areas=[
            "RESTful API design principles",
            "OpenAPI/Swagger specification",
            "Request/response validation",
            "API versioning strategies",
            "Rate limiting and security headers",
        ],
        communication_style="""Consumer-focused. You design APIs from the caller's perspective. 
You provide clear examples of requests and responses. You document edge cases.""",
        key_responsibilities=[
            "Design RESTful endpoints",
            "Define request/response schemas",
            "Implement proper HTTP status codes",
            "Create OpenAPI documentation",
            "Handle API versioning",
        ],
        constraints=[
            "Use proper HTTP methods (GET, POST, PUT, DELETE)",
            "Return appropriate status codes",
            "Validate all inputs",
            "Include pagination for lists",
            "Document all endpoints",
        ],
        output_format="""Provide:
- Endpoint definitions (method, path, description)
- Request/response schemas (Pydantic models)
- Example requests with curl
- Error response formats
- OpenAPI snippet if complex""",
        temperature=0.3,
        max_tokens=4096,
    ),
    
    # =========================================================================
    # FRONTEND
    # =========================================================================
    "frontend": SeedPrompt(
        agent_id="frontend",
        role_description="Frontend Engineer - React UI, user interactions, responsive design",
        personality="""You are a frontend specialist who creates intuitive, responsive interfaces. 
You think about user experience first - how does this feel to use? You write accessible, 
performant React code with proper state management.""",
        expertise_areas=[
            "React 18+ with hooks",
            "TypeScript for type safety",
            "Tailwind CSS for styling",
            "Responsive and accessible design",
            "State management (useState, useContext, Zustand)",
        ],
        communication_style="""User-focused and visual. You describe interfaces in terms of user 
interactions. You consider accessibility and mobile experience.""",
        key_responsibilities=[
            "Create React components",
            "Implement responsive layouts",
            "Handle user interactions and state",
            "Ensure accessibility (WCAG)",
            "Optimize for performance",
        ],
        constraints=[
            "Use TypeScript for all components",
            "Follow React best practices (hooks, composition)",
            "Ensure mobile responsiveness",
            "Include proper aria labels",
            "Keep components focused and reusable",
        ],
        output_format="""Provide:
- React component code (TypeScript)
- Props interface definitions
- Usage examples
- Responsive considerations
- Accessibility notes""",
        temperature=0.5,
        max_tokens=4096,
    ),
    
    # =========================================================================
    # QA
    # =========================================================================
    "qa": SeedPrompt(
        agent_id="qa",
        role_description="QA Engineer - Quality assurance, test planning, validation",
        personality="""You are a quality advocate who finds issues before users do. You think 
adversarially - how could this break? You systematically explore edge cases, boundary conditions, 
and unexpected inputs.""",
        expertise_areas=[
            "Test case design",
            "Edge case identification",
            "Regression testing strategy",
            "User acceptance criteria",
            "Bug reporting and reproduction",
        ],
        communication_style="""Methodical and thorough. You present test cases in clear categories. 
You explain why certain tests are critical. You provide reproduction steps for issues.""",
        key_responsibilities=[
            "Design test plans and cases",
            "Identify edge cases and boundaries",
            "Verify acceptance criteria",
            "Document found issues",
            "Prioritize testing efforts",
        ],
        constraints=[
            "Cover all acceptance criteria",
            "Test boundary conditions",
            "Include negative test cases",
            "Document reproduction steps",
            "Prioritize by risk",
        ],
        output_format="""Provide:
- Test plan overview
- Test cases (ID, description, steps, expected result)
- Edge cases to verify
- Priority ranking
- Any concerns or risks""",
        temperature=0.3,
        max_tokens=4096,
    ),
    
    # =========================================================================
    # TESTING
    # =========================================================================
    "testing": SeedPrompt(
        agent_id="testing",
        role_description="Test Automation Engineer - Unit tests, integration tests, coverage",
        personality="""You are a test automation expert who writes tests that catch bugs and document 
behavior. You follow TDD/BDD principles. You aim for meaningful coverage, not just high percentages.""",
        expertise_areas=[
            "pytest and fixtures",
            "Mocking and patching",
            "Integration testing",
            "Test coverage analysis",
            "BDD with Gherkin syntax",
        ],
        communication_style="""Code-first with clear test descriptions. You name tests to describe 
behavior. You explain what each test validates and why.""",
        key_responsibilities=[
            "Write unit tests for functions",
            "Create integration tests for workflows",
            "Set up test fixtures",
            "Mock external dependencies",
            "Achieve meaningful coverage",
        ],
        constraints=[
            "Test one behavior per test",
            "Use descriptive test names",
            "Mock external services",
            "Include both positive and negative cases",
            "Aim for 80%+ meaningful coverage",
        ],
        output_format="""Provide:
- pytest test files with fixtures
- Clear test function names (test_<behavior>_<condition>)
- Docstrings explaining intent
- Setup/teardown as needed
- Coverage considerations""",
        temperature=0.3,
        max_tokens=4096,
    ),
    
    # =========================================================================
    # SECURITY
    # =========================================================================
    "security": SeedPrompt(
        agent_id="security",
        role_description="Security Engineer - Vulnerability assessment, secure coding, authentication",
        personality="""You are a security specialist who thinks like an attacker to defend better. 
You identify vulnerabilities proactively. You balance security with usability - secure by default, 
but not so restrictive that users can't work.""",
        expertise_areas=[
            "OWASP Top 10 vulnerabilities",
            "Authentication (JWT, OAuth2)",
            "Input validation and sanitization",
            "Encryption and hashing",
            "Security headers and CORS",
        ],
        communication_style="""Risk-focused and practical. You explain vulnerabilities with impact 
and likelihood. You provide actionable fixes, not just warnings.""",
        key_responsibilities=[
            "Review code for security issues",
            "Design authentication flows",
            "Implement input validation",
            "Configure security headers",
            "Audit for common vulnerabilities",
        ],
        constraints=[
            "Never store passwords in plain text",
            "Validate and sanitize all inputs",
            "Use parameterized queries (no SQL injection)",
            "Implement proper CORS",
            "Follow principle of least privilege",
        ],
        output_format="""Provide:
- Security assessment with severity ratings
- Specific vulnerabilities found
- Recommended fixes with code
- Security configuration needed
- Authentication/authorization flow if relevant""",
        temperature=0.3,
        max_tokens=4096,
    ),
    
    # =========================================================================
    # DEVOPS
    # =========================================================================
    "devops": SeedPrompt(
        agent_id="devops",
        role_description="DevOps Engineer - CI/CD, containerization, infrastructure automation",
        personality="""You are a DevOps specialist who automates everything. You believe in 
infrastructure as code, reproducible builds, and continuous deployment. You optimize for 
developer experience and deployment safety.""",
        expertise_areas=[
            "Docker and multi-stage builds",
            "GitHub Actions workflows",
            "Kubernetes and Helm",
            "Terraform for infrastructure",
            "Monitoring and logging",
        ],
        communication_style="""Automation-focused and practical. You provide complete, working 
configurations. You explain the why behind each setting.""",
        key_responsibilities=[
            "Create Dockerfiles",
            "Set up CI/CD pipelines",
            "Configure deployment workflows",
            "Manage environment configurations",
            "Set up monitoring and alerts",
        ],
        constraints=[
            "Use multi-stage Docker builds",
            "Never hardcode secrets",
            "Include health checks",
            "Pin dependency versions",
            "Document environment requirements",
        ],
        output_format="""Provide:
- Dockerfile (multi-stage if appropriate)
- CI/CD workflow (GitHub Actions)
- Deployment configuration
- Environment variable documentation
- Required infrastructure""",
        temperature=0.3,
        max_tokens=4096,
    ),
    
    # =========================================================================
    # ARCHITECTURE
    # =========================================================================
    "architecture": SeedPrompt(
        agent_id="architecture",
        role_description="Solutions Architect - System design, patterns, scalability planning",
        personality="""You are a systems architect who designs for scale, maintainability, and 
evolution. You think in terms of bounded contexts, service boundaries, and data flows. You 
balance ideal architecture with practical constraints.""",
        expertise_areas=[
            "Microservices and service boundaries",
            "Event-driven architecture",
            "Domain-Driven Design",
            "Scalability patterns",
            "System integration strategies",
        ],
        communication_style="""Visual and conceptual. You use diagrams (described in text) to 
explain systems. You discuss trade-offs explicitly.""",
        key_responsibilities=[
            "Design system architecture",
            "Define service boundaries",
            "Plan data flows",
            "Identify scalability requirements",
            "Document architectural decisions",
        ],
        constraints=[
            "Consider operational complexity",
            "Plan for failure scenarios",
            "Document trade-offs",
            "Keep services appropriately sized",
            "Think about data consistency",
        ],
        output_format="""Provide:
- Architecture overview (text diagram)
- Component descriptions
- Data flow explanation
- Key design decisions with rationale
- Trade-offs considered
- Scalability considerations""",
        temperature=0.5,
        max_tokens=4096,
    ),
    
    # =========================================================================
    # DOCUMENTATION
    # =========================================================================
    "documentation": SeedPrompt(
        agent_id="documentation",
        role_description="Technical Writer - Documentation, tutorials, API guides",
        personality="""You are a documentation specialist who makes complex systems understandable. 
You write for your audience - beginners need more context, experts need reference. You believe 
good documentation is the difference between adoption and abandonment.""",
        expertise_areas=[
            "README and getting started guides",
            "API documentation",
            "Tutorial writing",
            "Architecture documentation",
            "Markdown and documentation tools",
        ],
        communication_style="""Clear and audience-appropriate. You use examples liberally. You 
structure content for scanning (headers, lists, code blocks).""",
        key_responsibilities=[
            "Write README files",
            "Document API endpoints",
            "Create tutorials and guides",
            "Document architecture decisions",
            "Maintain changelog",
        ],
        constraints=[
            "Include working code examples",
            "Write for the target audience",
            "Keep documentation up to date",
            "Use consistent formatting",
            "Include quick start guides",
        ],
        output_format="""Provide:
- Structured Markdown documentation
- Code examples that work
- Clear headings and sections
- Links to related docs
- Installation/setup instructions""",
        temperature=0.5,
        max_tokens=4096,
    ),
}


# =============================================================================
# AGENT REGISTRY - Central management
# =============================================================================

class AgentRegistry:
    """
    Central registry for agent identities and seed prompts.
    Supports custom agents and persistence.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".ainative" / "agents"
        self.identities: Dict[str, AgentIdentity] = DEFAULT_AGENT_IDENTITIES.copy()
        self.prompts: Dict[str, SeedPrompt] = DEFAULT_SEED_PROMPTS.copy()
        
        # Load custom agents
        if self.config_dir.exists():
            self._load_custom_agents()
    
    def _load_custom_agents(self):
        """Load custom agent definitions from config directory."""
        custom_file = self.config_dir / "custom_agents.yaml"
        if custom_file.exists():
            with open(custom_file) as f:
                custom = yaml.safe_load(f) or {}
                for agent_id, data in custom.items():
                    if "identity" in data:
                        self.identities[agent_id] = AgentIdentity(**data["identity"])
                    if "prompt" in data:
                        self.prompts[agent_id] = SeedPrompt(**data["prompt"])
    
    def get_identity(self, agent_id: str) -> AgentIdentity:
        """Get identity for an agent, with fallback."""
        if agent_id in self.identities:
            return self.identities[agent_id]
        # Fallback identity
        return AgentIdentity(
            id=agent_id,
            name=agent_id.title(),
            color=AgentColorPalette.MUTED,
            emoji="🤖",
        )
    
    def get_prompt(self, agent_id: str) -> Optional[SeedPrompt]:
        """Get seed prompt for an agent."""
        return self.prompts.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """List all available agent IDs."""
        return list(set(self.identities.keys()) | set(self.prompts.keys()))
    
    def save_custom_agent(self, identity: AgentIdentity, prompt: SeedPrompt):
        """Save a custom agent to config."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        custom_file = self.config_dir / "custom_agents.yaml"
        
        existing = {}
        if custom_file.exists():
            with open(custom_file) as f:
                existing = yaml.safe_load(f) or {}
        
        existing[identity.id] = {
            "identity": {
                "id": identity.id,
                "name": identity.name,
                "color": identity.color,
                "emoji": identity.emoji,
                "secondary_emoji": identity.secondary_emoji,
                "border_style": identity.border_style,
                "role_title": identity.role_title,
                "expertise": identity.expertise,
                "temperature": identity.temperature,
                "thinking_style": identity.thinking_style,
            },
            "prompt": prompt.to_dict(),
        }
        
        with open(custom_file, "w") as f:
            yaml.dump(existing, f, default_flow_style=False)
        
        self.identities[identity.id] = identity
        self.prompts[prompt.agent_id] = prompt


# =============================================================================
# REAL-TIME STREAMING RENDERER
# =============================================================================

class SwarmStreamRenderer:
    """
    Renders real-time swarm execution with color-coded parallel agent output.
    
    Designed for the Sub-Agent Orchestrator's coordinator + worker pattern.
    """
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.registry = AgentRegistry()
        self.active_agents: Dict[str, str] = {}  # agent_id -> current status
        self.iteration = 0
        self.max_iterations = 10
        self.start_time: Optional[datetime] = None
    
    def start_orchestration(self, task: str, agents: List[str], max_iterations: int = 10):
        """Display orchestration header and agent legend."""
        self.max_iterations = max_iterations
        self.start_time = datetime.now()
        
        # Task header
        self.console.print()
        self.console.print(Panel(
            f"[bold white]{task}[/]",
            title="🐝 [bold]Swarm Orchestration[/]",
            border_style="bright_white",
            box=DOUBLE,
        ))
        
        # Agent legend with colors
        self._print_agent_legend(agents)
        self.console.print()
    
    def _print_agent_legend(self, agents: List[str]):
        """Print color-coded legend of participating agents."""
        legend_parts = []
        for agent_id in agents:
            identity = self.registry.get_identity(agent_id)
            legend_parts.append(
                f"[{identity.color}]{identity.emoji} {identity.name}[/]"
            )
        
        legend = " │ ".join(legend_parts)
        self.console.print(f"[dim]Agents:[/] {legend}")
    
    def coordinator_thinking(self, thought: str):
        """Display coordinator's extended thinking."""
        identity = self.registry.get_identity("coordinator")
        self.console.print(
            f"\n[{identity.color}]{identity.emoji}[/] "
            f"[{identity.color} bold]{identity.name}[/] "
            f"[{AgentColorPalette.THINKING}]thinking...[/]"
        )
        self.console.print(f"   [dim italic]{thought}[/]")
    
    def coordinator_plan(self, plan_summary: str, tasks: List[Dict[str, str]]):
        """Display coordinator's execution plan."""
        identity = self.registry.get_identity("coordinator")
        
        # Plan header
        self.console.print(
            f"\n[{identity.color}]{identity.emoji}[/] "
            f"[{identity.color} bold]Execution Plan[/]"
        )
        
        # Task assignments
        for task in tasks:
            agent_id = task.get("agent", "unknown")
            agent_identity = self.registry.get_identity(agent_id)
            self.console.print(
                f"   [{agent_identity.color}]{agent_identity.emoji}[/] "
                f"[{agent_identity.color}]{agent_identity.name}[/]: "
                f"{task.get('description', 'No description')}"
            )
    
    def start_wave(self, wave_number: int, agents: List[str]):
        """Display start of parallel execution wave."""
        self.console.print()
        self.console.print(
            f"[bold white]━━━ Wave {wave_number} ━━━[/] "
            f"[dim]({len(agents)} agents in parallel)[/]"
        )
        
        # Show which agents are starting
        agent_chips = []
        for agent_id in agents:
            identity = self.registry.get_identity(agent_id)
            agent_chips.append(f"[{identity.color}]{identity.emoji}[/]")
        
        self.console.print(f"   Starting: {' '.join(agent_chips)}")
    
    def agent_started(self, agent_id: str, task_description: str):
        """Display agent starting work."""
        identity = self.registry.get_identity(agent_id)
        self.active_agents[agent_id] = "working"
        
        self.console.print(
            f"   [{identity.color}]{identity.emoji}[/] "
            f"[{identity.color}]{identity.name}[/] → "
            f"[dim]{task_description[:60]}{'...' if len(task_description) > 60 else ''}[/]"
        )
    
    def agent_progress(self, agent_id: str, message: str):
        """Display agent progress update."""
        identity = self.registry.get_identity(agent_id)
        secondary = identity.secondary_emoji or "→"
        
        self.console.print(
            f"      [{identity.color}]{secondary}[/] "
            f"[dim]{message}[/]"
        )
    
    def agent_completed(self, agent_id: str, success: bool, summary: str):
        """Display agent completion."""
        identity = self.registry.get_identity(agent_id)
        self.active_agents[agent_id] = "complete" if success else "failed"
        
        status_color = AgentColorPalette.SUCCESS if success else AgentColorPalette.ERROR
        status_icon = "✓" if success else "✗"
        
        self.console.print(
            f"   [{identity.color}]{identity.emoji}[/] "
            f"[{identity.color}]{identity.name}[/] "
            f"[{status_color}]{status_icon}[/] "
            f"[dim]{summary[:50]}{'...' if len(summary) > 50 else ''}[/]"
        )
    
    def agent_output(self, agent_id: str, content: str, title: Optional[str] = None):
        """Display agent output in a styled panel."""
        identity = self.registry.get_identity(agent_id)
        panel = identity.create_panel(
            content,
            title=title or f"Output",
            subtitle=f"[dim]{identity.name}[/]"
        )
        self.console.print(panel)
    
    def handoff(self, from_agent: str, to_agent: str, context: Optional[str] = None):
        """Display handoff between agents."""
        from_identity = self.registry.get_identity(from_agent)
        to_identity = self.registry.get_identity(to_agent)
        
        self.console.print(
            f"\n   [{from_identity.color}]{from_identity.emoji}[/] "
            f"[dim]→[/] "
            f"[{to_identity.color}]{to_identity.emoji}[/]"
            f"  [dim]{context or 'Handoff'}[/]"
        )
    
    def synthesis_started(self):
        """Display synthesis phase starting."""
        identity = self.registry.get_identity("coordinator")
        self.console.print()
        self.console.print(
            f"[{identity.color}]{identity.emoji}[/] "
            f"[{identity.color} bold]Synthesizing results...[/]"
        )
    
    def orchestration_complete(self, success: bool, metrics: Dict[str, Any]):
        """Display final orchestration summary."""
        self.console.print()
        
        # Calculate duration
        duration = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        # Status
        status_color = AgentColorPalette.SUCCESS if success else AgentColorPalette.ERROR
        status_icon = "✅" if success else "⚠️"
        status_text = "Complete" if success else "Incomplete"
        
        # Summary content
        summary_lines = [
            f"Duration: {duration:.1f}s",
            f"Agents used: {metrics.get('num_agents', 'N/A')}",
            f"Tasks completed: {metrics.get('tasks_completed', 'N/A')}",
            f"Parallelization: {metrics.get('parallelization_factor', 1.0):.1f}x",
        ]
        
        if metrics.get('tasks_failed', 0) > 0:
            summary_lines.append(f"Tasks failed: {metrics['tasks_failed']}")
        
        self.console.print(Panel(
            "\n".join(summary_lines),
            title=f"{status_icon} Orchestration {status_text}",
            border_style=status_color,
            box=DOUBLE,
        ))
    
    def parallel_status_display(self, agent_statuses: Dict[str, Dict[str, str]]):
        """
        Display parallel agent status in a live-updating grid.
        
        agent_statuses: {agent_id: {"status": str, "progress": str}}
        """
        columns = []
        for agent_id, status_info in agent_statuses.items():
            identity = self.registry.get_identity(agent_id)
            
            status = status_info.get("status", "idle")
            progress = status_info.get("progress", "")
            
            # Status indicator
            if status == "working":
                indicator = "⏳"
            elif status == "complete":
                indicator = "✓"
            elif status == "failed":
                indicator = "✗"
            else:
                indicator = "○"
            
            content = f"{indicator} {progress}" if progress else indicator
            
            columns.append(Panel(
                f"[{identity.color}]{content}[/]",
                title=f"{identity.emoji} {identity.name}",
                border_style=identity.color,
                width=20,
                height=3,
            ))
        
        self.console.print(Columns(columns, equal=True, expand=True))


# =============================================================================
# CLI COMMANDS
# =============================================================================

import click

@click.group(name="agents")
def agents_cli():
    """Manage agent identities and seed prompts."""
    pass


@agents_cli.command("list")
@click.option("--format", "output_format", type=click.Choice(["table", "json", "simple"]), 
              default="table", help="Output format")
def list_agents(output_format: str):
    """List all available agents with their visual identities."""
    console = Console()
    registry = AgentRegistry()
    
    if output_format == "json":
        output = {}
        for agent_id in registry.list_agents():
            identity = registry.get_identity(agent_id)
            output[agent_id] = {
                "name": identity.name,
                "emoji": identity.emoji,
                "color": identity.color,
                "role": identity.role_title,
            }
        click.echo(json.dumps(output, indent=2))
        return
    
    if output_format == "simple":
        for agent_id in sorted(registry.list_agents()):
            identity = registry.get_identity(agent_id)
            click.echo(f"{identity.emoji} {identity.name} ({agent_id})")
        return
    
    # Table format
    table = Table(
        title="🤖 Available Agents",
        show_header=True,
        header_style="bold white",
        border_style="dim",
    )
    table.add_column("Agent", style="bold")
    table.add_column("Role", style="dim")
    table.add_column("Style", justify="center")
    table.add_column("Temp", justify="right")
    
    for agent_id in sorted(registry.list_agents()):
        identity = registry.get_identity(agent_id)
        
        # Agent name with color
        name_text = Text(f"{identity.emoji} {identity.name}", style=identity.color)
        
        # Role
        role = identity.role_title[:35] + "..." if len(identity.role_title) > 35 else identity.role_title
        
        # Color swatch
        color_text = Text("███", style=identity.color)
        
        table.add_row(
            name_text,
            role,
            color_text,
            f"{identity.temperature}",
        )
    
    console.print(table)


@agents_cli.command("show")
@click.argument("agent_id")
@click.option("--prompt", "show_prompt", is_flag=True, help="Show full seed prompt")
@click.option("--json-output", is_flag=True, help="Output as JSON")
def show_agent(agent_id: str, show_prompt: bool, json_output: bool):
    """Show detailed information for a specific agent."""
    console = Console()
    registry = AgentRegistry()
    
    if agent_id not in registry.list_agents():
        raise click.ClickException(f"Unknown agent: {agent_id}")
    
    identity = registry.get_identity(agent_id)
    prompt = registry.get_prompt(agent_id)
    
    if json_output:
        output = {
            "identity": {
                "id": identity.id,
                "name": identity.name,
                "color": identity.color,
                "emoji": identity.emoji,
                "role_title": identity.role_title,
                "expertise": identity.expertise,
                "temperature": identity.temperature,
            },
            "prompt": prompt.to_dict() if prompt else None,
        }
        click.echo(json.dumps(output, indent=2))
        return
    
    # Identity panel
    identity_content = f"""[bold]Role:[/] {identity.role_title}
[bold]Color:[/] {identity.color}
[bold]Emoji:[/] {identity.emoji} / {identity.secondary_emoji or '—'}
[bold]Temperature:[/] {identity.temperature}
[bold]Thinking Style:[/] {identity.thinking_style}

[bold]Expertise:[/]
""" + "\n".join(f"  • {e}" for e in identity.expertise)
    
    console.print(Panel(
        identity_content,
        title=f"{identity.emoji} {identity.name}",
        border_style=identity.color,
        box=DOUBLE,
    ))
    
    if prompt:
        if show_prompt:
            console.print(Panel(
                prompt.to_system_prompt(),
                title="Seed Prompt",
                border_style="dim",
            ))
        else:
            console.print(f"\n[dim]Use --prompt to see the full seed prompt[/]")


@agents_cli.command("create")
@click.option("--interactive", "-i", is_flag=True, help="Interactive creation wizard")
@click.option("--from-yaml", type=click.Path(exists=True), help="Create from YAML file")
@click.option("--template", "-t", help="Base on existing agent")
def create_agent(interactive: bool, from_yaml: Optional[str], template: Optional[str]):
    """Create a new custom agent."""
    console = Console()
    registry = AgentRegistry()
    
    if from_yaml:
        with open(from_yaml) as f:
            data = yaml.safe_load(f)
        
        identity = AgentIdentity(**data.get("identity", {}))
        prompt = SeedPrompt(**data.get("prompt", {}))
        
        registry.save_custom_agent(identity, prompt)
        console.print(f"[green]✅ Agent '{identity.name}' created from {from_yaml}[/]")
        return
    
    if interactive:
        console.print("[bold]Create Custom Agent[/]\n")
        
        # Basic info
        agent_id = click.prompt("Agent ID (lowercase)", type=str).lower()
        name = click.prompt("Display name", default=agent_id.title())
        emoji = click.prompt("Emoji", default="🤖")
        color = click.prompt("Color (hex)", default="#74B9FF")
        role = click.prompt("Role title")
        
        # Use template as base if provided
        base_prompt = registry.get_prompt(template) if template else None
        
        # Create identity
        identity = AgentIdentity(
            id=agent_id,
            name=name,
            color=color,
            emoji=emoji,
            role_title=role,
        )
        
        # Create prompt (simplified for interactive)
        prompt = SeedPrompt(
            agent_id=agent_id,
            role_description=role,
            personality=click.prompt("Personality description"),
            expertise_areas=click.prompt("Expertise (comma-separated)").split(","),
            communication_style=click.prompt("Communication style"),
            key_responsibilities=click.prompt("Key responsibilities (comma-separated)").split(","),
            constraints=[],
            output_format="",
        )
        
        registry.save_custom_agent(identity, prompt)
        console.print(f"\n[green]✅ Agent '{name}' created![/]")
        console.print(f"[dim]Saved to: {registry.config_dir}[/]")
    else:
        console.print("Use --interactive or --from-yaml to create an agent")
        console.print("Example: ainative agents create --interactive")


@agents_cli.command("export")
@click.argument("agent_id")
@click.option("--output", "-o", type=click.Path(), help="Output file")
def export_agent(agent_id: str, output: Optional[str]):
    """Export agent definition to YAML."""
    registry = AgentRegistry()
    
    if agent_id not in registry.list_agents():
        raise click.ClickException(f"Unknown agent: {agent_id}")
    
    identity = registry.get_identity(agent_id)
    prompt = registry.get_prompt(agent_id)
    
    export_data = {
        "identity": {
            "id": identity.id,
            "name": identity.name,
            "color": identity.color,
            "emoji": identity.emoji,
            "secondary_emoji": identity.secondary_emoji,
            "border_style": identity.border_style,
            "role_title": identity.role_title,
            "expertise": identity.expertise,
            "temperature": identity.temperature,
            "thinking_style": identity.thinking_style,
        },
        "prompt": prompt.to_dict() if prompt else None,
    }
    
    yaml_output = yaml.dump(export_data, default_flow_style=False, sort_keys=False)
    
    if output:
        with open(output, "w") as f:
            f.write(yaml_output)
        click.echo(f"Exported to {output}")
    else:
        click.echo(yaml_output)


@agents_cli.command("preview")
@click.argument("agent_id")
def preview_agent(agent_id: str):
    """Preview how an agent appears in swarm output."""
    console = Console()
    registry = AgentRegistry()
    
    if agent_id not in registry.list_agents():
        raise click.ClickException(f"Unknown agent: {agent_id}")
    
    identity = registry.get_identity(agent_id)
    
    console.print(f"\n[bold]Preview: {identity.name}[/]\n")
    
    # Status line
    console.print(
        f"   [{identity.color}]{identity.emoji}[/] "
        f"[{identity.color}]{identity.name}[/] → "
        f"Processing task..."
    )
    
    # Progress
    console.print(
        f"      [{identity.color}]{identity.secondary_emoji or '→'}[/] "
        f"[dim]Analyzing requirements...[/]"
    )
    
    # Completion
    console.print(
        f"   [{identity.color}]{identity.emoji}[/] "
        f"[{identity.color}]{identity.name}[/] "
        f"[{AgentColorPalette.SUCCESS}]✓[/] "
        f"[dim]Task completed successfully[/]"
    )
    
    # Output panel
    console.print()
    console.print(identity.create_panel(
        "This is sample output from the agent.\nIt demonstrates the styled panel.",
        title="Sample Output"
    ))


# =============================================================================
# DEMO FUNCTION
# =============================================================================

def demo_parallel_execution():
    """Demonstrate parallel agent execution visualization."""
    console = Console()
    renderer = SwarmStreamRenderer(console)
    
    # Simulate orchestration
    renderer.start_orchestration(
        task="Build a REST API for user management with authentication",
        agents=["coordinator", "database", "api", "backend", "security", "testing"],
        max_iterations=5,
    )
    
    # Coordinator planning
    renderer.coordinator_thinking("Analyzing requirements... This is a multi-component system requiring database schema, API endpoints, business logic, security review, and tests.")
    
    renderer.coordinator_plan(
        "Parallel execution in 2 waves",
        tasks=[
            {"agent": "database", "description": "Design user schema with auth tables"},
            {"agent": "api", "description": "Define REST endpoints for users"},
            {"agent": "backend", "description": "Implement user service logic"},
            {"agent": "security", "description": "Review auth flow and token handling"},
            {"agent": "testing", "description": "Write test cases for user operations"},
        ]
    )
    
    # Wave 1 - Foundation
    import time
    renderer.start_wave(1, ["database", "api"])
    
    renderer.agent_started("database", "Design user and auth_token tables")
    renderer.agent_progress("database", "Creating users table with constraints...")
    time.sleep(0.5)
    renderer.agent_completed("database", True, "Schema with 2 tables, 3 indexes")
    
    renderer.agent_started("api", "Define CRUD endpoints for /users")
    renderer.agent_progress("api", "Designing request/response models...")
    time.sleep(0.3)
    renderer.agent_completed("api", True, "5 endpoints with OpenAPI spec")
    
    # Wave 2 - Implementation
    renderer.start_wave(2, ["backend", "security", "testing"])
    
    renderer.agent_started("backend", "Implement UserService class")
    renderer.agent_started("security", "Review authentication flow")
    renderer.agent_started("testing", "Create test fixtures")
    
    time.sleep(0.5)
    renderer.agent_progress("backend", "Implementing password hashing...")
    renderer.agent_progress("security", "Checking JWT configuration...")
    renderer.agent_progress("testing", "Writing user creation tests...")
    
    time.sleep(0.5)
    renderer.agent_completed("backend", True, "UserService with 8 methods")
    renderer.agent_completed("security", True, "No critical issues found")
    renderer.agent_completed("testing", True, "15 test cases, 92% coverage")
    
    # Synthesis
    renderer.synthesis_started()
    time.sleep(0.3)
    
    # Sample output
    renderer.agent_output(
        "backend",
        '''class UserService:
    async def create_user(self, data: UserCreate) -> User:
        """Create a new user with hashed password."""
        hashed = self.hash_password(data.password)
        return await self.repo.create(data, hashed)''',
        title="Generated Code"
    )
    
    # Complete
    renderer.orchestration_complete(True, {
        "num_agents": 5,
        "tasks_completed": 5,
        "tasks_failed": 0,
        "parallelization_factor": 2.3,
    })


if __name__ == "__main__":
    demo_parallel_execution()
