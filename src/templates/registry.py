from src.schemas.layouts import PageLayout, SectionBlueprint

# FAQ PAGE LAYOUT
FAQ_LAYOUT = PageLayout(
    layout_id="faq",
    page_type_name="Customer Support FAQ",
    description="A help center page resolving user queries.",
    structure=[
        SectionBlueprint(
            section_id="faq_intro",
            heading_default="Frequently Asked Questions",
            allowed_blocks=["text"],
            instructions="Write a reassuring intro paragraph about product safety and usage.",
            data_sources=["product.name"]
        ),
        SectionBlueprint(
            section_id="faq_grid",
            heading_default="Common Questions",
            allowed_blocks=["faq"],
            instructions="Map ALL 15 user questions provided in the context into this block.",
            data_sources=["questions"]
        )
    ]
)

# COMPARISON PAGE LAYOUT
COMPARISON_LAYOUT = PageLayout(
    layout_id="comparison",
    page_type_name="Head-to-Head Comparison",
    description="Objective analysis vs competitor.",
    structure=[
        SectionBlueprint(
            section_id="comp_intro",
            heading_default="Market Analysis",
            allowed_blocks=["text"],
            instructions="Briefly introduce the two contenders.",
            data_sources=["product.name", "competitor.name"]
        ),
        SectionBlueprint(
            section_id="comp_table",
            heading_default="Feature Breakdown",
            allowed_blocks=["table"],
            instructions="Compare Price, Ingredients, and Benefits in a structured table.",
            data_sources=["product", "competitor"]
        ),
        SectionBlueprint(
            section_id="comp_verdict",
            heading_default="Our Verdict",
            allowed_blocks=["text", "list"],
            instructions="Summarize why the primary product is the better value choice.",
            data_sources=["product.benefits"]
        )
    ]
)

# PRODUCT PAGE LAYOUT
PRODUCT_LAYOUT = PageLayout(
    layout_id="product",
    page_type_name="Product Detail Page",
    description="Marketing landing page.",
    structure=[
        SectionBlueprint(
            section_id="hero",
            heading_default="Product Overview",
            allowed_blocks=["text"],
            instructions="High-energy marketing hook describing the product.",
            data_sources=["product.description"]
        ),
        SectionBlueprint(
            section_id="benefits",
            heading_default="Key Benefits",
            allowed_blocks=["list"],
            instructions="List the key value propositions as bullet points.",
            data_sources=["product.benefits"]
        ),
        SectionBlueprint(
            section_id="usage",
            heading_default="How to Use",
            allowed_blocks=["list"],
            instructions="Step-by-step usage guide.",
            data_sources=["product.how_to_use"]
        )
    ]
)

TEMPLATE_REGISTRY = {
    "faq": FAQ_LAYOUT,
    "comparison": COMPARISON_LAYOUT,
    "product": PRODUCT_LAYOUT
}
