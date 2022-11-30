import React, { useEffect, useState } from 'react'
import '../App.css'

export default function EndpointHealth(props) {
    const [isLoaded, setIsLoaded] = useState(false);
    const [log, setLog] = useState(null);
    const [error, setError] = useState(null);

    const getHealth = () => {
        fetch(`http://bryan-rainbow-lab6a-acit3855.eastus.cloudapp.azure.com:8120/health`)
            .then(res => res.json())
            .then((result)=>{
                console.log("Received Heath results")
                setLog(result);
                setIsLoaded(true);
            },(error) => {
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
        const interval = setInterval(() => getHealth(), 20000); // Update every 20 seconds
        return() => clearInterval(interval);
    }, [getHealth]);

    if (error) {
        return (<div className={"error"}>Error foudn when fetching from API</div>)
    } else if (isLoaded === false) {
        return (<div>Loading...</div>)
    } else if (isLoaded === true) {

        return (
            <div>
                <h3>Health Stats</h3>
                {JSON.stringify(log)}
            </div>
        )
    }
}