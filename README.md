# calculator_api
2nd homework of Python and Linux adaptation course


## Usage

### Making a Calculation Request

You can perform calculations by sending a POST request to the `/calculate` endpoint with a JSON body containing the expression.

#### Using `curl`
- Open a terminal or command prompt.
- Use the following `curl` command: curl -X POST http://127.0.0.1:5000/calculate -H "Content-Type: application/json" -d "{"expression":"[your-expression]"}"

#### Using Postman
- Open Postman and create a new request.
- Set the method to POST and the URL to `http://127.0.0.1:5000/calculate`.
- In the "Headers" section, add `Content-Type` as `application/json`.
- In the "Body" section, select `raw` and input your JSON data:
{
    "expression": "[your-expression]"
}
