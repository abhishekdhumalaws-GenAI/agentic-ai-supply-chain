# supply_chain_workflow_stack.py

from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
)
from constructs import Construct

class SupplyChainWorkflowStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # --- 1️⃣ Reference already deployed Lambdas by name ---
        planner_lambda = _lambda.Function.from_function_name(
            self, "PlannerLambda", function_name="planner_lambda"
        )

        executor_lambda = _lambda.Function.from_function_name(
            self, "ExecutorLambda", function_name="executor_lambda"
        )

        analyst_lambda = _lambda.Function.from_function_name(
            self, "AnalystLambda", function_name="analyst_lambda"
        )

        # --- 2️⃣ Step Function tasks ---
        planner_task = tasks.LambdaInvoke(
            self, "Planner Task",
            lambda_function=planner_lambda,
            output_path="$.Payload"
        )

        executor_task = tasks.LambdaInvoke(
            self, "Executor Task",
            lambda_function=executor_lambda,
            output_path="$.Payload"
        )

        analyst_task = tasks.LambdaInvoke(
            self, "Analyst Task",
            lambda_function=analyst_lambda,
            output_path="$.Payload"
        )

        # --- Optional feedback loop: Analyst → Planner ---
        feedback_choice = sfn.Choice(self, "Feedback required?")
        feedback_choice.when(
            sfn.Condition.boolean_equals("$.feedback_required", True),
            planner_task
        )
        feedback_choice.otherwise(sfn.Succeed(self, "Workflow Completed"))

        # --- 3️⃣ Define workflow sequence ---
        definition = planner_task.next(executor_task).next(analyst_task).next(feedback_choice)

        # --- 4️⃣ Create Step Function ---
        state_machine = sfn.StateMachine(
            self, "SupplyChainStateMachine",
            definition=definition,
            timeout=Duration.minutes(10)
        )

        # --- 5️⃣ Create S3 bucket trigger ---
        input_bucket = s3.Bucket(self, "SupplyChainInputBucket")

        # Trigger Step Function when a new file is uploaded
        input_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.SfnDestination(state_machine)
        )
