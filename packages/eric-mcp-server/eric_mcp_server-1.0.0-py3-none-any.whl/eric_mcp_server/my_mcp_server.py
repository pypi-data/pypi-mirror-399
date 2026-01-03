from fastmcp import FastMCP, Context
import requests
import base64
import urllib.parse
import uuid
import json
import os

mcp = FastMCP(name="File Processing Server", version="1.0.5" )

@mcp.tool
async def process_file(url: str, ctx: Context) -> dict:
    """ Receive a file from a public HTTP/HTTPS URL or Local File, encode it as base64, 
    and submit it to the ICR document processing service for analysis.

    Args:
        url (str): The full file:// or HTTP or HTTPS URL of the file to be processed. 
                   Must point to a publicly accessible resource. 
                   Example: "https://example.com/invoice.pdf" or "file://d:/temp/1.png"

    Returns:
        dict: A JSON object containing either:
              - 'result': The response from the processing service (success)
              - 'error': An error message if download or processing failed

    Raises:
        ValueError: If the URL scheme is not http/https
        requests.Timeout: If download or service call times out
    """
    try:
        # Generate trace ID
        trace_id = str(uuid.uuid4())
        # Extract filename from URL
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme == 'file':
            # Local file path
            file_path = urllib.parse.unquote(parsed.path)
            await ctx.info(f"读取文件：{file_path}")
           
            filename = os.path.basename(file_path)
            await ctx.info(f"文件名：{filename}")
           
            with open(file_path, 'rb') as f:
                content = f.read()
        else:
            # Remote URL
            filename = os.path.basename(parsed.path)
            response = requests.get(url)
            response.raise_for_status()
            content = response.content
            
        # Convert to base64
        encoded_content = base64.b64encode(content).decode('utf-8')
        
        # Create Data_Cntnt
        data_cntnt = {
            "channelCode": "icrProduct",
            "traceId": trace_id,
            "serviceId": "1966055986389057536",
            "fileName": filename
        }
        
        # Submit to service
        service_url = "http://localhost:8080/service/withFileBase64"
        payload = {
            "Data_Cntnt": json.dumps(data_cntnt, ensure_ascii=False),
            "fileBase64": encoded_content
        }
        
        headers = {'channel_api_key':'eyJ0eXAiOiJKV1QiLCJ0eXBlIjoiSldUIiwiYWxnIjoiSFMyNTYifQ.eyJjaGFubmVsTmFtZSI6IklDUuS6p-WTgSIsInR5cGUiOiJjaGFubmVsX2FwaV9rZXkiLCJjaGFubmVsQ29kZSI6ImljclByb2R1Y3QifQ.g0aCjiQ3hgfbsuYQIWUvJVh3AFBz1ogvfBli0ypDaxw',
                   'Host':'demo.app.dev'}
        response = requests.post(service_url, data=payload, headers=headers)
        response.raise_for_status()
        
        return {"result": response.json()}
        
    except Exception as e:
        return {"error": str(e)}
    
def main():
    print("Hello from my MCP server!")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()