"""Tests for invoice functionality"""

from fastbotty.core.config import InvoiceConfig, LabeledPrice


class TestInvoiceConfig:
    """Tests for InvoiceConfig model"""

    def test_basic_invoice_config(self):
        """Test basic invoice configuration"""
        invoice = InvoiceConfig(
            title="Product Name",
            description="Product description",
            payload="product_123",
            currency="USD",
            prices=[
                LabeledPrice(label="Item Price", amount=1000),
                LabeledPrice(label="Tax", amount=100),
            ],
        )
        assert invoice.title == "Product Name"
        assert invoice.description == "Product description"
        assert invoice.payload == "product_123"
        assert invoice.currency == "USD"
        assert len(invoice.prices) == 2
        assert invoice.prices[0].label == "Item Price"
        assert invoice.prices[0].amount == 1000

    def test_invoice_with_optional_fields(self):
        """Test invoice configuration with optional fields"""
        invoice = InvoiceConfig(
            title="Product Name",
            description="Product description",
            payload="product_123",
            currency="USD",
            prices=[LabeledPrice(label="Price", amount=1000)],
            provider_token="",  # Empty string for Telegram Stars
            max_tip_amount=500,
            suggested_tip_amounts=[100, 200, 500],
            start_parameter="start_param",
            photo_url="https://example.com/photo.jpg",
            photo_width=800,
            photo_height=600,
            need_name=True,
            need_email=True,
            need_phone_number=False,
            need_shipping_address=False,
        )
        assert invoice.provider_token == ""
        assert invoice.max_tip_amount == 500
        assert invoice.suggested_tip_amounts == [100, 200, 500]
        assert invoice.start_parameter == "start_param"
        assert invoice.photo_url == "https://example.com/photo.jpg"
        assert invoice.need_name is True
        assert invoice.need_email is True

    def test_invoice_with_flexible_pricing(self):
        """Test invoice with flexible pricing (requires shipping address)"""
        invoice = InvoiceConfig(
            title="Product Name",
            description="Product description",
            payload="product_123",
            currency="USD",
            prices=[LabeledPrice(label="Base Price", amount=1000)],
            need_shipping_address=True,
            is_flexible=True,
        )
        assert invoice.need_shipping_address is True
        assert invoice.is_flexible is True

    def test_labeled_price(self):
        """Test LabeledPrice model"""
        price = LabeledPrice(label="Test Item", amount=2500)
        assert price.label == "Test Item"
        assert price.amount == 2500

    def test_multiple_prices(self):
        """Test invoice with multiple price breakdowns"""
        invoice = InvoiceConfig(
            title="Complete Order",
            description="Order with multiple items",
            payload="order_456",
            currency="EUR",
            prices=[
                LabeledPrice(label="Item 1", amount=1000),
                LabeledPrice(label="Item 2", amount=1500),
                LabeledPrice(label="Shipping", amount=500),
                LabeledPrice(label="Discount", amount=-200),
            ],
        )
        assert len(invoice.prices) == 4
        assert invoice.prices[3].amount == -200  # Discount as negative amount

    def test_invoice_with_template_strings_in_amount(self):
        """Test invoice configuration with template strings in amount field"""
        invoice = InvoiceConfig(
            title="Product Name",
            description="Product description",
            payload="product_123",
            currency="USD",
            prices=[
                LabeledPrice(label="Item Price", amount="{{ total_price|int }}"),
                LabeledPrice(label="Tax", amount="{{ tax_amount|int }}"),
            ],
        )
        assert invoice.prices[0].amount == "{{ total_price|int }}"
        assert invoice.prices[1].amount == "{{ tax_amount|int }}"

    def test_invoice_with_template_strings_in_max_tip(self):
        """Test invoice configuration with template strings in max_tip_amount"""
        invoice = InvoiceConfig(
            title="Product Name",
            description="Product description",
            payload="product_123",
            currency="USD",
            prices=[LabeledPrice(label="Price", amount=1000)],
            max_tip_amount="{{ max_tip|int }}",
        )
        assert invoice.max_tip_amount == "{{ max_tip|int }}"

    def test_invoice_with_template_strings_in_suggested_tips(self):
        """Test invoice configuration with template strings in suggested_tip_amounts"""
        invoice = InvoiceConfig(
            title="Product Name",
            description="Product description",
            payload="product_123",
            currency="USD",
            prices=[LabeledPrice(label="Price", amount=1000)],
            suggested_tip_amounts=["{{ tip1|int }}", "{{ tip2|int }}", 500],
        )
        assert invoice.suggested_tip_amounts == ["{{ tip1|int }}", "{{ tip2|int }}", 500]

    def test_invoice_with_mixed_int_and_string_amounts(self):
        """Test invoice with both integer and template string amounts"""
        invoice = InvoiceConfig(
            title="Mixed Order",
            description="Order with mixed pricing",
            payload="order_789",
            currency="USD",
            prices=[
                LabeledPrice(label="Fixed Price", amount=1000),
                LabeledPrice(label="Dynamic Price", amount="{{ dynamic_price|int }}"),
            ],
        )
        assert invoice.prices[0].amount == 1000
        assert invoice.prices[1].amount == "{{ dynamic_price|int }}"
