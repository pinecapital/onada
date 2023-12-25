## buy 
`[{"symbol":"EUR_USD","units":"100","side":"buy"}]`

## sell 
`[{"symbol":"EUR_USD","units":"100","side":"sell"}]`

## exit 
`[{"symbol":"EUR_USD","exit":"true"}]`

### configurations
put the account id and api key 

## start 
`sudo gunicorn -w 4 -b 0.0.0.0:80 main:app`