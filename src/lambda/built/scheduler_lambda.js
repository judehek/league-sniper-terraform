"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handler = void 0;
const aws_sdk_1 = require("aws-sdk");
exports.handler = async (event) => {
    let parsed = JSON.parse(event.body);
    console.log(event.body);
    if (parsed) {
        var ecs = new aws_sdk_1.default.ECS();
        return {
            statusCode: 200,
            body: "Successfully started ECS task!"
        };
    }
    return {
        statusCode: 500,
        body: "Could not parse input body!"
    };
};
//# sourceMappingURL=scheduler_lambda.js.map