from jsonschema import validate
import api_helpers
import schemas
from hamcrest import assert_that, contains_string

def test_patch_order_by_id():

    # Create Order First
    create_response = api_helpers.post_api_data(
        "/store/order",
        {"pet_id": 0}
    )

    assert create_response.status_code == 201
    order = create_response.json()
    validate(instance=order, schema=schemas.order)

    order_id = order["id"]

    # PATCH Order
    patch_response = api_helpers.patch_api_data(
        f"/store/order/{order_id}",
        {"status": "sold"}
    )

    assert patch_response.status_code == 200
    assert_that(
        patch_response.json()["message"],
        contains_string("updated successfully")
    )
