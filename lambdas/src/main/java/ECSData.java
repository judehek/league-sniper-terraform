public class ECSData {
    public final String cluster;
    public final String subnet;
    public final String taskDefinition;

    public ECSData(String cluster, String subnet, String taskDefinition) {
        this.cluster = cluster;
        this.subnet = subnet;
        this.taskDefinition = taskDefinition;
    }
}
