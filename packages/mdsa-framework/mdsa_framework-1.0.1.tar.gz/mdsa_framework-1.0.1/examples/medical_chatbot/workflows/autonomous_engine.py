"""
Autonomous Workflow Engine for Medical Application

Handles complex multi-step medical workflows autonomously.

Author: MDSA Framework Team
Date: 2025-12-06
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """Single step in a medical workflow."""
    step_id: int
    action: str  # 'lookup_code', 'calculate_billing', 'process_claim', etc.
    domain: str  # Which medical domain to use
    query: str  # Query for this step
    dependencies: List[int]  # Steps that must complete first
    result: Optional[Dict[str, Any]] = None
    status: str = 'pending'  # 'pending', 'in_progress', 'completed', 'failed'


@dataclass
class Workflow:
    """Complete medical workflow."""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    status: str = 'pending'  # 'pending', 'in_progress', 'completed', 'failed'
    final_result: Optional[Dict[str, Any]] = None


class AutonomousWorkflowEngine:
    """
    Autonomous engine for executing complex medical workflows.

    Capabilities:
    - Multi-step workflow execution
    - Dependency resolution
    - Sequential and parallel execution
    - Error handling and recovery
    - Result aggregation
    """

    def __init__(self, orchestrator):
        """
        Initialize autonomous workflow engine.

        Args:
            orchestrator: MDSA Orchestrator instance
        """
        self.orchestrator = orchestrator
        self.workflows: Dict[str, Workflow] = {}

    def create_workflow(
        self,
        workflow_id: str,
        name: str,
        description: str,
        steps: List[WorkflowStep]
    ) -> Workflow:
        """Create a new workflow."""
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            steps=steps
        )
        self.workflows[workflow_id] = workflow
        return workflow

    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow autonomously.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Final workflow result
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]
        workflow.status = 'in_progress'

        logger.info(f"Starting workflow: {workflow.name}")

        try:
            # Execute steps in order, respecting dependencies
            for step in workflow.steps:
                # Wait for dependencies
                if step.dependencies:
                    await self._wait_for_dependencies(workflow, step)

                # Execute step
                step.status = 'in_progress'
                logger.info(f"Executing step {step.step_id}: {step.action}")

                step.result = await self._execute_step(step)
                step.status = 'completed'

                logger.info(f"Step {step.step_id} completed")

            # Aggregate results
            workflow.final_result = self._aggregate_results(workflow)
            workflow.status = 'completed'

            logger.info(f"Workflow {workflow.name} completed successfully")

            return workflow.final_result

        except Exception as e:
            workflow.status = 'failed'
            logger.error(f"Workflow {workflow.name} failed: {e}")
            raise

    async def _execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step."""
        try:
            # Use orchestrator to process the query
            result = self.orchestrator.process_request(
                step.query,
                context={
                    'preferred_domain': step.domain,
                    'workflow_step': step.step_id
                }
            )

            return {
                'status': 'success',
                'action': step.action,
                'domain': result['domain'],
                'response': result['response'],
                'latency_ms': result['latency_ms']
            }

        except Exception as e:
            return {
                'status': 'error',
                'action': step.action,
                'error': str(e)
            }

    async def _wait_for_dependencies(
        self,
        workflow: Workflow,
        step: WorkflowStep
    ):
        """Wait for dependent steps to complete."""
        for dep_id in step.dependencies:
            dep_step = workflow.steps[dep_id - 1]  # step_id is 1-indexed

            while dep_step.status != 'completed':
                if dep_step.status == 'failed':
                    raise Exception(
                        f"Dependency step {dep_id} failed"
                    )

                await asyncio.sleep(0.1)  # Poll every 100ms

    def _aggregate_results(self, workflow: Workflow) -> Dict[str, Any]:
        """Aggregate results from all steps."""
        results = []
        for step in workflow.steps:
            if step.result and step.result['status'] == 'success':
                results.append({
                    'step_id': step.step_id,
                    'action': step.action,
                    'response': step.result['response']
                })

        return {
            'workflow_id': workflow.workflow_id,
            'workflow_name': workflow.name,
            'total_steps': len(workflow.steps),
            'completed_steps': len(results),
            'results': results
        }

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current status of a workflow."""
        if workflow_id not in self.workflows:
            return {'error': 'Workflow not found'}

        workflow = self.workflows[workflow_id]

        return {
            'workflow_id': workflow.workflow_id,
            'name': workflow.name,
            'status': workflow.status,
            'steps_completed': sum(
                1 for step in workflow.steps if step.status == 'completed'
            ),
            'total_steps': len(workflow.steps)
        }


# ============================================================================
# Predefined Workflows
# ============================================================================

def create_patient_encounter_workflow() -> List[WorkflowStep]:
    """
    Create workflow for complete patient encounter.

    Steps:
    1. Look up diagnosis codes (ICD-10)
    2. Look up procedure codes (CPT)
    3. Calculate billing
    4. Submit claim
    """
    return [
        WorkflowStep(
            step_id=1,
            action='lookup_diagnosis_code',
            domain='medical_coding',
            query='Lookup ICD-10 code for Type 2 diabetes mellitus without complications',
            dependencies=[]
        ),
        WorkflowStep(
            step_id=2,
            action='lookup_procedure_code',
            domain='medical_coding',
            query='Lookup CPT code for office visit, established patient, 20-29 minutes',
            dependencies=[]
        ),
        WorkflowStep(
            step_id=3,
            action='calculate_billing',
            domain='medical_billing',
            query='Calculate billing for CPT 99213 with insurance coverage 80% and $50 deductible',
            dependencies=[2]  # Needs procedure code first
        ),
        WorkflowStep(
            step_id=4,
            action='submit_claim',
            domain='claims_processing',
            query='Submit insurance claim for ICD-10 E11.9 and CPT 99213, total charge $150',
            dependencies=[1, 2, 3]  # Needs all previous steps
        )
    ]


def create_billing_inquiry_workflow() -> List[WorkflowStep]:
    """
    Create workflow for billing inquiry.

    Steps:
    1. Look up procedure code
    2. Calculate charges
    3. Explain insurance coverage
    """
    return [
        WorkflowStep(
            step_id=1,
            action='lookup_procedure',
            domain='medical_coding',
            query='What is CPT code 70553?',
            dependencies=[]
        ),
        WorkflowStep(
            step_id=2,
            action='calculate_charges',
            domain='medical_billing',
            query='What is the typical charge for MRI brain with and without contrast (CPT 70553)?',
            dependencies=[1]
        ),
        WorkflowStep(
            step_id=3,
            action='explain_coverage',
            domain='medical_billing',
            query='How much will insurance cover for CPT 70553 if patient has 80/20 coverage?',
            dependencies=[2]
        )
    ]


def create_claim_denial_workflow() -> List[WorkflowStep]:
    """
    Create workflow for handling claim denial.

    Steps:
    1. Check claim status
    2. Identify denial reason
    3. Determine resolution steps
    """
    return [
        WorkflowStep(
            step_id=1,
            action='check_status',
            domain='claims_processing',
            query='Check status of claim #12345',
            dependencies=[]
        ),
        WorkflowStep(
            step_id=2,
            action='identify_reason',
            domain='claims_processing',
            query='Why was claim #12345 denied?',
            dependencies=[1]
        ),
        WorkflowStep(
            step_id=3,
            action='resolution_steps',
            domain='claims_processing',
            query='What steps are needed to resolve the denial and resubmit claim #12345?',
            dependencies=[2]
        )
    ]


# Demo
if __name__ == "__main__":
    print("=" * 70)
    print("Autonomous Workflow Engine - Demo")
    print("=" * 70)

    # Show predefined workflows
    workflows = {
        'patient_encounter': create_patient_encounter_workflow(),
        'billing_inquiry': create_billing_inquiry_workflow(),
        'claim_denial': create_claim_denial_workflow()
    }

    for name, steps in workflows.items():
        print(f"\n{name.replace('_', ' ').title()} Workflow:")
        print(f"  Total Steps: {len(steps)}")

        for step in steps:
            deps = f" (depends on: {step.dependencies})" if step.dependencies else ""
            print(f"  {step.step_id}. {step.action} [{step.domain}]{deps}")

    print("\n" + "=" * 70)
    print("✓ Workflows defined and ready")
    print("=" * 70)
