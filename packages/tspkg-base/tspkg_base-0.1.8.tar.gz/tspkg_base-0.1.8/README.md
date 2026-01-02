# tspkg_base

Secondary development platform base for Python applications.

> Provides AOP, Hook, and Rewrite capabilities, allowing external business packages to dynamically take over, rewrite,
> or enhance the execution logic of original methods without modifying the original project code.

## Installation

```bash
pip install tspkg_base
# or
pip install tspkg_base==0.1.0 -i https://pypi.org/simple
```

## Usage

### Your Project

### Example code

- bootstrap code
    - This code is necessary because it loads the tspkg package.

```python
from tspkg_base.runtime.bootstrap import bootstrap

result = bootstrap(tspkg_dir=tspkg_dir)
logger.info(f"Bootstrap result: {result['loaded']} loaded, {result['failed']} failed")

```

- entry code

```python
from tspkg_base import aop_entry


# Usage example
@aop_entry(key="order.create")
def create_order(user_id: int, product_id: int, quantity: int = 1) -> dict:
    """
    Create order (original method)

    This method is decorated with @aop_entry and can be taken over or enhanced
    by rewrite methods in secondary development packages.
    """
    logger.info(f"Creating order: user_id={user_id}, product_id={product_id}, quantity={quantity}")

    # Simulate order creation logic
    order_id = 10000 + user_id  # Simple order ID generation

    result = {
        "order_id": order_id,
        "user_id": user_id,
        "product_id": product_id,
        "quantity": quantity,
        "status": "created",
        "created_by": "original_code"
    }

    logger.info(f"Order created: {result}")
    return result

```

### Secondary Development Project

### Project's directory

```
your_business_pkg/
├── code/                    # required：Python source code
│   ├── __init__.py
│   └── your_module.py      # your rewrite code
└── ...                      # other[optional]
```

#### Example code

```python
from tspkg_base.aop.decorators import rewrite
from tspkg_base.aop.context import ExecutionContext


@rewrite(target="order.create", mode="around")
def my_create_order(ctx: ExecutionContext):
    """
    Rewrite order creation logic

    This rewrite method will completely take over the execution of the original method.
    """
    # Get original method arguments
    args = ctx.get_args()
    kwargs = ctx.get_kwargs()

    user_id = args[0] if len(args) > 0 else kwargs.get('user_id')
    product_id = args[1] if len(args) > 1 else kwargs.get('product_id')
    quantity = args[2] if len(args) > 2 else kwargs.get('quantity', 1)

    # You can do some preprocessing here
    # For example: parameter validation, permission checks, etc.
    if user_id <= 0:
        return {
            "error": "Invalid user_id",
            "user_id": user_id
        }

    # Call original method
    original_result = ctx.call_original()

    # Modify result
    original_result["modified_by_rewrite"] = True
    original_result["rewrite_message"] = "This order was created with rewrite logic"
    original_result["rewrite_version"] = "1.0.0"

    # You can add additional business logic
    # For example: send notifications, log records, etc.

    return original_result
```

## Pack Secondary Development Project

- Please zip your project directory and rename the file extension from zip to tspkg.
- Note that the directory compressed using zip software is not encrypted, but it can meet most scenarios.
- This software supports encryption keys. If you need further assistance, please contact the author

## UnPack Secondary Development Project

- It should be noted that if you have specified the tspkg directory in your program, simply place tspkg in this
  directory. In short, they must be consistent.

```python
# The directory parameter for loading tspkg is specified by tspkg_dir

result = bootstrap(tspkg_dir=tspkg_dir)
```

## Features

- AOP (Aspect-Oriented Programming) support
- Hook mechanism
- Method rewriting (Rewrite) capability
- Dynamic code injection

## License

MIT License

## FAQ

### Q: How to know the signature of the original method?

A: You need to confirm with the original project development team, or check the original project documentation. The
rewrite code should be compatible with the original method signature.

### Q: Can rewrite call other modules?

A: Yes, but please note:

- Ensure that dependent modules are available in the original project
- Avoid importing internal modules of the original project (may cause version conflicts)
- It is recommended to only use standard library and known third-party libraries

### Q: Will multiple rewrites conflict?

A: Each `target` can only have one rewrite. If multiple TSPKG packages contain the same `target`, the later loaded one
will override the earlier one.

### Q: How to update rewrite?

A: Repackage the TSPKG file, replace the original file, and then restart the original project.
