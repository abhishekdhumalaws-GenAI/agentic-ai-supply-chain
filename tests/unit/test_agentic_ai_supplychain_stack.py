import aws_cdk as core
import aws_cdk.assertions as assertions

from agentic_ai_supplychain.agentic_ai_supplychain_stack import AgenticAiSupplychainStack

# example tests. To run these tests, uncomment this file along with the example
# resource in agentic_ai_supplychain/agentic_ai_supplychain_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AgenticAiSupplychainStack(app, "agentic-ai-supplychain")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
