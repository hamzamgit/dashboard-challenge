import os.path

from RPA.PDF import PDF
from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from config import OUTPUT, URL
import datetime


class Process:

    def __init__(self):
        """
        Initialize required classes instances and required variables for complete process.
        """
        self.browser = Selenium()
        self.files = Files()
        self.agencies_data = []
        self.headers = []
        self.table_data = []
        self.pdf = PDF()

    def open_site(self):
        """
        Open web browser and navigate to the itdashboard.org
        :return:
        """
        self.browser.set_download_directory(OUTPUT)
        self.browser.open_available_browser(URL, maximized=True)

    def scrap_all_agencies(self):
        """
        click on DIVE IN and get all the agency names and amounts.
        :return:
        """
        self.browser.wait_until_page_contains("DIVE IN")
        self.browser.find_element('//a[@href="#home-dive-in"]').click()
        self.browser.wait_until_page_contains_element('//a[contains(@href,"/drupal/summary")]//span')
        agencies_list = self.browser.find_elements('//a[contains(@href,"/drupal/summary")]//span')
        for i in range(0, len(agencies_list), 2):
            if i < len(agencies_list):
                self.agencies_data.append({"Agency Name": agencies_list[i].text, "Amount": agencies_list[i + 1].text})
            else:
                self.agencies_data.append({"Agency Name": agencies_list[i-1].text, "Amount": agencies_list[i].text})

    def write_agencies_to_workbook(self):
        """
        write the agency names and amounts to the workbook with worksheet named agencies
        :return:
        """
        self.files.create_workbook(f"{OUTPUT}/Agencies.xlsx")
        self.files.remove_worksheet("Sheet")
        self.files.create_worksheet("Agencies")
        self.files.append_rows_to_worksheet(self.agencies_data, header=True, name="Agencies")
        self.files.save_workbook()
        self.files.close_workbook()

    def get_headers(self):
        """
        Get headers of UII table of agency
        :return:
        """
        headers = self.browser.find_elements('//div[@id="investments-table-object_wrapper"]//th')
        for head in headers:
            if head.text != '':
                self.headers.append(head.text)

    def scrap_agency_table(self, agency_name):
        """
        scrap agency table with name provided in the params
        :param agency_name:
        :return:
        """
        self.browser.find_element(f'//span[text()="{agency_name}"]').click()
        self.browser.wait_until_page_contains_element('//div[@id="investments-table-object_wrapper"]',
                                                      timeout=datetime.timedelta(seconds=60))
        self.get_headers()
        self.browser.select_from_list_by_value('//select[@name="investments-table-object_length"]', '-1')
        total_entries = int(self.browser.find_element('//div[@class="dataTables_info"]').text.split(" ")[-2])
        self.browser.wait_until_page_contains_element(
            f'//div[@id="investments-table-object_wrapper"]//tr[{total_entries}]', timeout=datetime.timedelta(seconds=20))
        rows = self.browser.find_elements('//div[@id="investments-table-object_wrapper"]//tr')
        pdf_code = ''
        pdf_name = ''
        for row in rows:
            table_entry = {}
            for count, column in enumerate(row.find_elements_by_tag_name("td")):
                if column.text == "":
                    break
                else:
                    try:
                        pdf_url = column.find_element_by_tag_name("a").get_attribute("href")
                    except:
                        pdf_url = None
                    if pdf_url:
                        code = column.text
                        self.get_pdf(pdf_url, code)
                        pdf_code, pdf_name = self.read_pdf(code)
                    table_entry[self.headers[count]] = column.text
            if not len(table_entry) == 0:
                if table_entry["UII"] in pdf_code and table_entry["Investment Title"] in pdf_name:
                    table_entry["pdf_matched"] = "Matched"
                else:
                    table_entry["pdf_matched"] = "Not Matched"
                self.table_data.append(table_entry)

    def write_table_to_workbook(self):
        """
        Write the scraped UII agency table to worksheet named Individual Investments
        :return:
        """
        self.files.open_workbook(f"{OUTPUT}/Agencies.xlsx")
        self.files.create_worksheet("Individual Investments")
        self.files.append_rows_to_worksheet(self.table_data, header=True, name="Individual Investments")
        self.files.save_workbook()
        self.files.close_workbook()

    def get_pdf(self, url, code):
        """
        Download pdf from url given in params and store it as name "code.pdf" in output folder
        :param url:
        :param code:
        :return:
        """
        self.browser.execute_javascript(f'window.open("{url}");')
        tabs = self.browser.get_window_handles()
        self.browser.switch_window(tabs[-1])
        self.browser.wait_until_page_contains_element('//a[text()="Download Business Case PDF"]',
                                                      timeout=datetime.timedelta(seconds=15))
        self.browser.find_element('//a[text()="Download Business Case PDF"]').click()
        while True:
            if os.path.exists(f"{OUTPUT}/{code}.pdf"):
                break
            else:
                pass
        self.browser.close_window()
        self.browser.switch_window(tabs[0])

    def read_pdf(self, code):
        """
        read pdf first page section A with name "code.pdf" and retrieve investment name and UII code.
        :param code:
        :return:
        """
        text = self.pdf.get_text_from_pdf(f"{OUTPUT}/{code}.pdf", 1)
        pdf_name = text[1].split("Name of this Investment:")[1].split(".")[0]
        pdf_code = text[1].split("(UII):")[1].split("Section")[0]
        return pdf_code, pdf_name
