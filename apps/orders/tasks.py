from celery import shared_task


@shared_task
def send_low_stock_alert(
    store_name,
    product_title,
    quantity
):

    print(
        "\n"
        "=========================\n"
        "LOW STOCK ALERT\n"
        f"Store: {store_name}\n"
        f"Product: {product_title}\n"
        f"Remaining Quantity: {quantity}\n"
        "=========================\n"
    )

    return True