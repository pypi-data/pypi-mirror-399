from behave_auto_docstring import given


@given("A Fediverse application")
def a_fediverse_application(context):
    assert context.fediverse_application


@given("the object parsing is build")
async def build_object_parsing(context):
    context.object_parsing = await context.fediverse_application.build_object_parsing(
        context.session
    )
    assert context.object_parsing
