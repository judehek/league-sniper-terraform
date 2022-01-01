import com.amazonaws.lambda.thirdparty.com.google.gson.Gson;
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.ecs.EcsClient;
import software.amazon.awssdk.services.ecs.model.*;

import java.io.*;
import java.nio.charset.Charset;

public class LambdaHandler implements RequestStreamHandler {
    private Gson gson = new Gson();

    @Override
    public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context) {
        PrintWriter writer = new PrintWriter(
                new BufferedWriter(new OutputStreamWriter(outputStream, Charset.forName("US-ASCII"))));
        BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream, Charset.forName("US-ASCII")));
        ECSData ecsData = gson.fromJson(reader, ECSData.class);
        LambdaLogger logger = context.getLogger();

        EcsClient ecsClient = EcsClient.builder()
                .region(Region.US_EAST_2)
                .build();
        logger.log("here1");
        AwsVpcConfiguration vpcConfiguration = AwsVpcConfiguration.builder()
                .assignPublicIp(AssignPublicIp.ENABLED)
                .subnets(ecsData.subnet)
                .build();

        logger.log("here2");
        NetworkConfiguration networkConfiguration = NetworkConfiguration.builder()
                .awsvpcConfiguration(vpcConfiguration)
                .build();

        logger.log("here3");
        RunTaskRequest runTaskRequest = RunTaskRequest.builder()
                .cluster(ecsData.cluster)
                .networkConfiguration(networkConfiguration)
                .taskDefinition(ecsData.taskDefinition)
                .launchType(LaunchType.FARGATE)
                .count(1)
                .build();

        try {
            logger.log("here4");
            RunTaskResponse result = ecsClient.runTask(runTaskRequest);
            logger.log("start container response: " + result);
            writer.println("success");
        } catch (Exception e) {
            logger.log("start container response error: " + e);
            writer.println("error");
            writer.println(e);
        }

    }
}
