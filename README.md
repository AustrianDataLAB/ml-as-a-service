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
Work in progress

### Budget Estimation

# Microsoft Azure Estimate

| Service category | Service type              | Custom name | Region      | Description                                                                                                                                                                                                                                                                                                         | Estimated monthly cost | Estimated upfront cost |
|------------------|---------------------------|-------------|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------:|-----------------------:|
| Compute          | Azure Kubernetes Service (AKS) |             | West Europe | Kostenlos (nicht für Produktionsumgebungen); Die Clusterverwaltung ist kostenlos.; 2 A2 v2 (2 vCPUs, 4 GB RAM) x 730 Stunden (Nutzungsbasierte Bezahlung), Linux; 0 verwaltete Betriebssystemdatenträger – E1                                                                                                          | €115.55                | €0.00                  |
| Speicher         | Storage Accounts          |             | West Europe | Block Blob Storage, Allgemein v2, Hierarchischer Namespace, LRS Redundanz, Zugriffsebene: Heiß, Kapazität: 1.000 GB - Nutzungsbasierte Bezahlung, 10 x 10 000 Schreibvorgänge, 10 x 10 000 Lesevorgänge, 10 x 10 000 iterative Lesevorgänge, 10 x 100 iterative Schreibvorgänge, 1.000GB Datenabruf, 1.000GB Datenschreibvorgänge, SFTP deaktiviert, 1.000 GB Index, 1 x 10 000 Andere Vorgänge | €45.56                 | €0.00                  |
|                  | **Total**                 |             |             |                                                                                                                                                                                                                                                                                                                     | **€161.11**            | €0.00                  |

---

#### Disclaimer

This estimate was created at 3/24/2024 9:36:07 AM UTC.



