# ML as a Service

In the ever-changing, data-driven world we live in, new possibilities emerge every day, especially in the realm of research. While expert knowledge is often required to fully benefit from these opportunities, we aim to provide everyone interested in working with this data an easy-to-use, out-of-the-box model capable of leveraging provided data for classification and regression tasks. Specifically for the academic/education sector, users should be able to upload data and select a pre-defined model to get started and utilize basic computing power. Scaling, availability, and accessibility are provided by us, abstracting the technical components from the domain(-expert) user, allowing them to concentrate on gaining further insights into interesting topics.

## Product
### Value Proposition
Further details can be found in our [value proposition](https://docs.google.com/document/d/1FxX3pmvXWAWQ9-dPw1ywX_qll5r7SFyholCQi2ff00U/edit?usp=sharing).

### Userexperience sketch
To complement the value proposition, we tried to illustrate the user experience through sketching, allowing for a better understanding of this product

![user experience sketch](./docs/UX-sketch.jpeg "Userexperience sketch")

### Architecture
![architecture sketch](./docs/arch-sketch.png "Architecture sketch")

### Roadmap

#### Phase 1: Initial Setup - 07.04
- **Requirement Analysis**
- **Microservice Architecture Planning**
- **TensorFlow (TF) Setup**

#### Phase 2: Core Development - 31.05
- **Persistence Service Development**
- **Model Serving Service Development**
- **Gateway Service Development**
- **Frontend (FE) Development**
- **Kubernetes Pod Spawning and Scaling Setup**

#### Phase 3: Integration and Testing - 15.06
- **Microservices Integration**
- **System Testing**


### Budget Estimation

# Microsoft Azure Estimate

| Service category | Service type                | Custom name | Region      | Description                                                                                                                                                                                                                                                                                          | Estimated monthly cost | Estimated upfront cost |
|------------------|-----------------------------|-------------|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------:|-----------------------:|
| Compute          | Azure Kubernetes Service (AKS) |             | West Europe | Free (not for production environments); Cluster management is free; 2 A2 v2 (2 vCPUs, 4 GB RAM) x 730 hours (pay-as-you-go), Linux; 0 managed OS disks – E1                                                                                                                                                               | €115.55                | €0.00                  |
| Storage          | Storage Accounts            |             | West Europe | Block Blob Storage, General Purpose v2, Hierarchical Namespace, LRS Redundancy, Access Tier: Hot, Capacity: 1,000 GB - Pay-as-you-go, 10 x 10,000 write operations, 10 x 10,000 read operations, 10 x 10,000 list operations, 10 x 100 other operations, 1,000GB data retrieval, 1,000GB data write operations, SFTP disabled, 1,000 GB index, 1 x 10,000 other operations | €45.56                 | €0.00                  |
|                  | **Total**                   |             |             |                                                                                                                                                                                                                                                                                                      | **€161.11**            | €0.00                  |

---


#### Disclaimer

This estimate was created at 3/24/2024 9:36:07 AM UTC.



