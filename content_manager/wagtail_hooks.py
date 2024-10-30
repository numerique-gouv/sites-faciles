from wagtail import hooks


# Doesn't remove everything if used from the dashboard app
@hooks.register("construct_homepage_summary_items")
def remove_all_summary_items(request, items):
    items.clear()
