import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.ecs.EcsClient;
import software.amazon.awssdk.services.ecs.model.*;

public class LambdaHandler implements RequestHandler<ECSData, String> {
    private final Logger logger = LoggerFactory.getLogger(getClass());

    @Override
    public String handleRequest(ECSData ecsData, Context context) {
        EcsClient ecsClient = EcsClient.builder()
                .region(Region.US_EAST_2)
                .build();

        AwsVpcConfiguration vpcConfiguration = AwsVpcConfiguration.builder()
                .assignPublicIp(AssignPublicIp.ENABLED)
                .subnets(ecsData.subnet)
                .build();

        NetworkConfiguration networkConfiguration = NetworkConfiguration.builder()
                .awsvpcConfiguration(vpcConfiguration)
                .build();

        RunTaskRequest runTaskRequest = RunTaskRequest.builder()
                .cluster(ecsData.cluster)
                .networkConfiguration(networkConfiguration)
                .taskDefinition(ecsData.taskDefinition)
                .launchType(LaunchType.FARGATE)
                .count(1)
                .build();

        try {
            RunTaskResponse result = ecsClient.runTask(runTaskRequest);
            logger.info("start container response: " + result);
            return "success";
        } catch (Exception e) {
            logger.error("start container response error: ", e);
            return "error\n" + e.toString();
        }

    }
}
