

error_codes = {
  200:"OK",
  404: "Page Not Found",
  403: "Unauthorized"
}


server_ips = {
  # "EC2_8081":"http://15.206.0.116:8081",
  "EC2_8082":"http://15.206.0.116:8082",
  # "EC2_8080":"http://15.206.0.116:8080",
  "Stage": "https://stage-open-data.aws.ondc.org/",
  "Prod":"https://open-data.aws.ondc.org/"
}

django_apis = {
  "max_date": "http://15.206.0.116:8081/api/get-max-date/",
  "overall_data" : "http://15.206.0.116:8081/api/retail/overall/top_card_delta/?domainName=None&startDate=2024-02-27&endDate=2024-05-26",
  "mapwise_data": "http://15.206.0.116:8081/api/retail/overall/map_statewise_data/?domainName=None&startDate=2024-02-27&endDate=2024-05-26"
}

