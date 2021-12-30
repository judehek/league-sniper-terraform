import {APIGatewayProxyEvent, APIGatewayProxyResult} from "aws-lambda";
import AWS from 'aws-sdk';

export const handler = async (
    event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
    let parsed = JSON.parse(event.body);
    console.log(event.body)
    if (parsed) {
        var ecs = new AWS.ECS();

        return {
            statusCode: 200,
            body: "Successfully started ECS task!"
        }
    }
    return {
        statusCode: 500,
        body: "Could not parse input body!"
    }
}