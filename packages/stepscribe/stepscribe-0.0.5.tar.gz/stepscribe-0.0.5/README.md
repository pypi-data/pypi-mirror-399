<div align="center"> <img src="https://raw.githubusercontent.com/DataVimDev/StepScribe/main/logo.png" alt="Step Scribe logo" width="200"> </div>

A package to write AWS Step Function state machines using python and output valid AWS states language JSON or to various visualization formats.

## Installation
```pip install stepscribe```

## Examples
Here's a simple task example that invokes an existing lambda function:
```python
from stepscribe import Task

if __name__ == "__main__":
    get_price = Task(
                    name="Get Current Price",
                    next_='Check Price',
                    resource="arn:aws:states:::lambda:invoke",
                    arguments={'Payload': {"product": "{% $states.context.Execution.Input.product %}"},
                        'FunctionName': "arn:aws:lambda:<region>:account-id:function:priceWatcher:$LATEST",
                    },
                    assign={'currentPrice': "{% $states.result.Payload.current_price %}"}
    )
    print(get_price)               
```

This python code generates the following Amazon states language JSON:

```json
"Get Current Price": {
  "Type": "Task",
  "QueryLanguage" : "JSONata",
  "Resource": "arn:aws:states:::lambda:invoke",
  "Next": "Check Price",
  "Arguments": {
    "Payload": {
    "product": "{% $states.context.Execution.Input.product %}"
    },
    "FunctionName": "arn:aws:lambda:<region>:account-id:function:priceWatcher:$LATEST"
  },
  "Assign": {
    "currentPrice": "{% $states.result.Payload.current_price %}"
  }
}
```

The value of StepScribe comes from leveraging python to create or compose objects and then generate the corresponding JSON. For example, what if we wanted to get the current price of a product, check if it's on sale, and check our inventory. If each of these actions is a lambda, we now need 3 tasks like above, but with different names and lambda functions, and each of these to be a branch of a parallel state.

```python
from stepscribe import Task, Parallel

def product_task(name: str, lambda_name: str) -> Task:
    output=name.lower().replace(' ', '_').replace('get_', '')

    return Task(
                name=name,
                next_='Check Price',
                resource="arn:aws:states:::lambda:invoke",
                arguments={'Payload': {"product": "{% $states.context.Execution.Input.product %}"},
                        'FunctionName': f"arn:aws:lambda:<region>:account-id:function:{lambda_name}:$LATEST",
                },
                assign={'currentPrice': f"{{% $states.result.Payload.{output} %}}"}
    )


if __name__ == "__main__":

    tasks = [("Get Current Price", "priceWatcher"), ("Check Sale", "isOnSale"), ("Get Current Inventory", "inventoryWatcher")]
    step_function = Parallel(
                        name="Product Check",
                        branches=[product_task(task[0], task[1]) for task in tasks)]
                        )
    print(step_function)
```
This allows for considerable consolidation of the boilerplate and becomes more valuable if custom retry, catcher, item readers, or other components are reused across large state machines.

## Roadmap
Currently, StepScribe has python dataclasses for states and major components and assumes only JSONata is being used (not JSONPath state attributes or query language) and writes these objects to the corresponding states language JSON.

The following features are planned:
- [ ] Test coverage and documentation
- [ ] JSONPath support
- [ ] Write state machine to mermaidJS diagram
- [ ] Read state machine
- [ ] JSONata expression validation

Usage, desired features, bug reports, bug fixes, and feature implementations are welcome.

## Contributing
For feature requests or bug reports, please submit an issue in GitHub with as much information as possible.

For bug fixes or feature implementations, fork the repo and create a PR to merge your fork branch here and request a review from me. See the contributions guide for more information.

## License
MIT

## Origin
My first use of AWS Step Functions seemed simple: a small set of parallel branches, most being short sequences of distributed map states that invoked a lambda on particular items of a large JSON data set in S3 or did partical aggregation of results from previous states. The JSON defining the state machine quickly grew to over 1000 lines when formatted, with massive amount of duplication (each branch was basically the same but invoked a different set of lambdas - so the same item reader, processor, writer and internal states inside each distributed map, just different state names and lambda arns). Furthermore, I needed to have a dev and prod version of this that would stay in sync. I also needed visual versions that could be used in documentation and presentations. 

It seemed like a better approach would be to use python to generate versions of the state machine json, allowing loops and f-strings to easily construct machine with redundant structures and to generate dev, prod, or visuals from the same base state machine definition.
