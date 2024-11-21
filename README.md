# Vietnamese Company Information Scraper

A Python-based web scraping tool designed to extract comprehensive business information from Vietnamese company registries, primarily from masothue.com.

## Features

- Extract company information using name or tax ID
- Retrieve comprehensive business details including:
  - Company Name
  - Tax ID
  - Main Industry
  - Legal Representative
  - Address
  - Phone Number
  - Website and Email (when available)
- Multi-threaded execution for improved performance
- Robust error handling and fallback mechanisms
- Support for Vietnamese character encoding

## Technologies

- Python 3.x
- Key Libraries:
  - `requests`: For making HTTP requests
  - `beautifulsoup4`: For HTML parsing
  - `lxml`: Fast XML and HTML parser
  - `urllib3`: HTTP client
  - `concurrent.futures`: For multi-threading support

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jamesnq/crawl-company-masothue.git
cd crawl-company-masothue
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Run the script with a company name as an argument:

```bash
python src/main.py "CÔNG TY TNHH EXAMPLE"
```

If no company name is provided, it will use a default example company.

### Output Format

The script will output company information in the following format:

```
Thông tin doanh nghiệp:
--------------------------------------------------
Tên công ty: [Company Name]
Mã số thuế: [Tax ID]
Ngành nghề chính: [Main Industry]
Người đại diện: [Legal Representative]
Địa chỉ: [Address]
Số điện thoại: [Phone Number]
Email: [Email if available]
Website: [Website if available]
--------------------------------------------------
Thời gian thực thi: [Execution Time] giây
```

## Notes

- The script respects website rate limits and implements delays between requests
- Some company information might not be available or accessible
- Website structure changes may affect scraping functionality

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](https://github.com/jamesnq/crawl-company-masothue/issues).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**James Nguyen**
- GitHub: [@jamesnq](https://github.com/jamesnq)

## Acknowledgments

- masothue.com for providing company information
- All contributors who help improve this tool
