public class ECSData {
    public String cluster;
    public String subnet;
    public String taskDefinition;

    public ECSData(String cluster, String subnet, String taskDefinition) {
        this.cluster = cluster;
        this.subnet = subnet;
        this.taskDefinition = taskDefinition;
    }


    public String getCluster() {
        return cluster;
    }

    public void setCluster(String cluster) {
        this.cluster = cluster;
    }

    public String getSubnet() {
        return subnet;
    }

    public void setSubnet(String subnet) {
        this.subnet = subnet;
    }

    public String getTaskDefinition() {
        return taskDefinition;
    }

    public void setTaskDefinition(String taskDefinition) {
        this.taskDefinition = taskDefinition;
    }
}
