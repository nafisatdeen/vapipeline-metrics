
# vapipeline-metrics
To export the metrics from video analytics pipeline to prometheus 

To build a docker image after making changes, use the following command from the root folder:  
`sudo docker build --tag <image_name> . `

If not, the available image : uvdeployment/shield:prometheus_metrics will be used.

To deploy it, use  
`sudo helm install <name the chart or use --generate-name> charts `

To deploy it on a specific node:  
`sudo helm install <name the chart or use --generate-name> charts  --set nodeSelector.<node label>=<node-label vale>`

Check whether the chart is deployed using :   
`sudo helm ls`

To uninstall the chart:
`sudo helm uninstall <name the chart>`

  
The view the metrics use:  
 ` curl localhost:9877 `
