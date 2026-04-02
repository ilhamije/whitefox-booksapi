## API Endpoints
```
https://b9dq8x89pj.execute-api.us-east-1.amazonaws.com/docs
https://b9dq8x89pj.execute-api.us-east-1.amazonaws.com/api/books
https://b9dq8x89pj.execute-api.us-east-1.amazonaws.com/api/books/{id}
```

## TEST
### Test it on the browser
Open https://b9dq8x89pj.execute-api.us-east-1.amazonaws.com/docs and try the endpoints

### run the unit tests and integration test
```
pytest -v
```
### test it with CURL
List the books
```
curl -X GET https://b9dq8x89pj.execute-api.us-east-1.amazonaws.com/api/books
```

Create new book
```
curl -X POST https://b9dq8x89pj.execute-api.us-east-1.amazonaws.com/api/books \
  -H "Content-Type: application/json" \
  -d '{"title": "The Great Gatsby", "author": "F. Scott Fitzgerald"}'
```

Get book by id
```
curl -X GET https://b9dq8x89pj.execute-api.us-east-1.amazonaws.com/api/books/{id}
```


## AWS Deployment

### Install Serverless Framework
```
npm install -g serverless
```

### Install Serverless Plugins
Install the python requirements plugin used in `serverless.yml`:
```
serverless plugin install -n serverless-python-requirements
```

### Configure AWS Credentials
Ensure your AWS credentials are set up appropriately:
```
aws configure
```

### Deploy
Deploy the service to your AWS account:
```
serverless deploy
```

## Local Deployment

### Fireup Docker for DynamoDB
```
docker run -d -p 8000:8000 --name dynamodb-local amazon/dynamodb-local
```
(make sure you already have docker desktop running)

### Install AWS CLI
You can install the AWS CLI via Homebrew on macOS:
```
brew install awscli
```
### Create DynamoDB table
```
aws dynamodb create-table \
    --table-name booksapi-local-books \
    --attribute-definitions AttributeName=pk,AttributeType=S \
    --key-schema AttributeName=pk,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url http://localhost:8000
```

### Check DynamoDB table
```
aws dynamodb list-tables --endpoint-url http://localhost:8000
```

### Run FastAPI app on another terminal
```
ENV=local uvicorn src.main:app --reload
```

