import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://bryan-rainbow-lab6a-acit3855.eastus.cloudapp.azure.com:8100/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Daily Sales</th>
							<th>Deliveries</th>
						</tr>
						<tr>
							<td># Total daily sales events: {stats['num_daily_sales_events']}</td>
							<td># Total delivery events: {stats['num_delivery_events']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Cheeseburgers Sold: {stats['max_cheeseburgers_sold']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Fry Servings Sold: {stats['max_fry_servings_sold']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Fry Boxes Received: {stats['max_fry_boxes_received']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
