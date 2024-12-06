

Nexios provides a way to define and validate schemas for various types of data. It is designed to allow users to define fields in schemas, apply validation rules to those fields, and handle validation errors efficiently.

### Overview

Nexios Validators allows the creation of `Schema` classes with fields of different types, including strings, integers, booleans, URLs, JSON, files, and images. Each field type can be customized with validation rules, and you can define custom validation methods for your fields.

### Key Components

1. **SchemaMeta**: The metaclass used to define schemas. It dynamically adds field descriptors to the schema.
2. **BaseSchema**: A base class for all schemas, providing initialization and error-handling features.
3. **FieldDescriptor**: This is used to define the rules and validation logic for each field in the schema.
4. **Field Types**: These include:
   - `StringField`
   - `IntegerField`
   - `BooleanField`
   - `URLField`
   - `JSONField`
   - `FileField`
   - `ImageField`
   - `ListField`

### How to Use the Library

#### 1. Define a Schema

To define a schema, inherit from the `Schema` class and add fields using descriptors. Each field can have validation rules like `required`, `max_length`, `min_length`, etc.

```python
from nexios.validator import Schema, fields

class UserSchema(Schema):
    name = fields.StringField(max_length=50, min_length=3)
    age = fields.IntegerField(min=18, max=100)
```

#### 2. Instantiate the Schema

Once the schema is defined, you can create an instance of the schema and validate data by calling the schema.

```python
user_data = {
    'name': 'John Doe',
    'age': 25
}

user_schema = UserSchema()
await user_schema(user_data)
```

#### 3. Validating Data

You can use the `validate` method to validate the fields. If there are validation errors, you can access them via the `validation_errors` property.

```python
if user_schema.is_valid():
    print("Data is valid!")
else:
    print("Validation errors:", user_schema.validation_errors)
```

#### 4. Custom Field Validation

You can define custom validation methods for each field in the schema. The method should be named `validate_<field_name>` and should accept a value to validate.

```python
class UserSchema(Schema):
    name = FieldDescriptor(StringField(max_length=50, min_length=3))
    age = FieldDescriptor(IntegerField(min=18, max=100))

    async def validate_name(self, value):
        # Custom validation for the 'name' field
        if value == "Admin":
            raise ValidationError("Name 'Admin' is not allowed.")
        return value
```

#### 5. Accessing Validated Data

After validation, you can access the validated data through the `validated_data` property.

```python
print(user_schema.validated_data)
```

### Field Types and Validation Rules

- **StringField**
  - Validates string length using `max_length` and `min_length`.
  - Can validate the required field with `required=True`.
  
- **IntegerField**
  - Validates integer values, including checks for `min` and `max` values.

- **BooleanField**
  - Validates boolean values, converting common truthy/falsy values to Python `True` or `False`.

- **URLField**
  - Validates if the input is a valid URL.

- **JSONField**
  - Validates if the input is a valid JSON (either a string or dictionary).

- **FileField & ImageField**
  - Validates file uploads, checking file type and size.
  - `ImageField` specifically allows image file types (e.g., `.jpg`, `.png`).

- **ListField**
  - Validates if the input is a list and applies validation to each item in the list using a specified child field.

### Error Handling

When validation fails, a `ValidationError` is raised. The error details are stored in the `validation_errors` property of the schema.

#### Example:

```python
user_data = {
    'name': 'Jo',
    'age': 15
}

user_schema = UserSchema()
await user_schema(user_data)

if not user_schema.is_valid():
    print(user_schema.validation_errors)
```

Output:

```
{
    'name': ['Value length must not be below 3'],
    'age': ['Value must not be below 18']
}
```

### Example of Full Schema Definition

```python
class UserSchema(Schema):
    name = FieldDescriptor(fields.StringField(max_length=50, min_length=3))
    email = FieldDescriptor(fields.StringField(),required=True)
    age = FieldDescriptor(fields.IntegerField(min=18, max=100),default = 19)
    is_active = FieldDescriptor(fields.BooleanField(),default = False)
    profile_image = FieldDescriptor(fields.ImageField(),required = False)

    async def validate_email(self, value):
        if "example.com" in value:
            raise ValidationError("Email domain 'example.com' is not allowed.")
        return value
```

### Advanced Usage

#### 1. Custom Field Types

You can create custom field types by inheriting from `BaseField` and implementing the `validate` method. For example:

```python
class CustomField(BaseField):
    async def validate(self, value):
        # Custom validation logic here
        return value
```

#### 2. Using Multiple Schemas

You can use multiple schemas in a parent-child relationship. For example, you can create a schema for nested data:

```python
class AddressSchema(Schema):
    street = FieldDescriptor(StringField())
    city = FieldDescriptor(StringField())
    country = FieldDescriptor(StringField())

class UserSchema(Schema):
    name =  FieldDescriptor(StringField(),required = False)
    address = FieldDescriptor(AddressSchema())
```

### Example with handlers 

```py
from nexios import get_application
from nexios.validator import Schema,FieldDescriptor, fields
app = get_application()

class PostSchema(Schema):
    name = FieldDescriptor(fields.StringField(max_length = 120))
    cataegory = FieldDescriptor(fields.ListField(
        child_field = fields.StringField()
    ))
    detail = FieldDescriptor(fields.StringField(max_length = 120))

    async def validate_name(self, value):

        check = await check_database()
        if check.exists():
            raise ValueError("Post with this title")

        return value
@app.post("/create")
async def create_post(request, response):
    post_schema = PostSchema()
    await post_schema(await request.json()) #call the validator instance
    if not post_schema.is_valid():
        response.status(400)
        return response.json(post_schema.validation_errors)

    await create_post(**post_schema.validated_data)
    return response.json({"detail":"post added succesfully"},status = 201)


```