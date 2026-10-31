
from workflow import run_business_workflow


def generate_business_report(
    sales_data,
    inventory_data,
    review_text,
    client
):

    return run_business_workflow(
        sales_data,
        inventory_data,
        review_text,
        client
    )
