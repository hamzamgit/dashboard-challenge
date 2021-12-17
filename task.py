from libraries.challenge import Process
from config import OUTPUT, create_dir


def main():
    it_dashboard = Process()
    it_dashboard.open_site()
    it_dashboard.scrap_all_agencies()
    it_dashboard.write_agencies_to_workbook()
    it_dashboard.scrap_agency_table("Social Security Administration")
    it_dashboard.write_table_to_workbook()


if __name__ == "__main__":
    create_dir(OUTPUT)
    main()
