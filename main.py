from parse_api.parse_requests import parse_page


if __name__ == "__main__":
    url = "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id" \
          "=182714625642338&sort_data[direction]=desc&sort_data[" \
          "mode]=relevancy_monthly_grouped&search_type=page&media_type=all "
    parse_page(url=url, filters={})
