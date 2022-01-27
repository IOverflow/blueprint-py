# This is where controllers lives.

*Define  controllers logic (splitted into routes) in files in this folder*
*Provide the imports in the __init__.py file so we can then access controllers in the following
way:*

```python
import controllers

app.add_routes(controllers.users)
```