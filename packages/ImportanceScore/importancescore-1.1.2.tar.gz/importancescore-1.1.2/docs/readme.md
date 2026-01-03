
# ImportanceScore

**ImportanceScore** is a configurable ML based tool suite designed to create a meaningful importance score by applying either 
supervised machine learning or explicit, rule-based logic.
**ImportanceScore**  externalizes all configuration to  ensure your scoring process
is **automated, repeatable, and scalable**.

> Note: for a detailed usage guide for the GUI, see the [Usage Guide](docs/usage.md).

### Key Benefits

*   **Reproducible Pipeline:** A config driven system and a `tune -> train -> predict` workflow ensure every run is repeatable. The system is designed 
for version control (e.g., Git), allowing you to archive configurations and model artifacts together for long-term reproducibility.  
* **Prescriptive Directories and File Names** To ensure clarity and reproducibility, **ImportanceScore** uses a standardized directory structure and file naming 
convention. This design allows you to define the logic for a category once and apply it to any number of different data segments.
*   **Transparent & Tunable:** The system is built for the iterative loop of "score -> explain -> tune." Detailed logging, feature contribution 
reports (`--explain`), and a fully configuration-driven design allow you to build trust in your model and refine its logic with precision. A GUI is provided
to make this process quick and easy.
* **Drop-in Models:** Because of its structured nature you can very easily switch between models.  This includes the ability to start with the
rule-based Weighted Linear Model, use it to create training data, and then switch to the more powerful Random Forest Regressor.
* **Scoring-Specific Features:** The tool includes a powerful preprocessing pipeline with features specifically tailored for creating importance scores:
    *   **`text_weight_scoring`**: Assign bonus points based on keywords.
    *   **`feature_interactions`**: Combine related features (e.g., `historic`, `heritage`) to prevent double-counting.
    *   **`clip_outliers`**: Cap feature values at absolute thresholds based on domain knowledge.
*   **Regional Context Scoring:** The system allows you to score distinct geographic regions independently while using a shared logic configuration. This is critical for highlighting locally significant 
* features that would otherwise be overshadowed in a global ranking.
  *   *Example:* **Mt. Mitchell (2,037m)** is the towering giant of the Appalachians and a major landmark. However, if scored directly against the 4,000m peaks of the Rockies, it would appear 
  * insignificant. By scoring regions separately (e.g., `East_Peaks`, `West_Peaks`), the system correctly identifies Mt. Mitchell as a "Tier 1" feature *within its context*, ensuring it appears 
  * prominently on the map.
  *   *Requirement:* To use this feature, you simply provide separate input files for each region (e.g., `peaks_east.csv`, `peaks_west.csv`) and run the scoring pipeline for each file individually.

  
---

#### Directory Structure

This system uses
two key organizing concepts: **`category`** and **`segment`**.

*   **`category`**: A reusable blueprint for a *type* of data (e.g., `peaks`, `poi`).
*   **`segment`**: A specific *subset* of data being processed (e.g., `uswest`, `yellowstone`).

The project layout separates reusable configurations from segment-specific data:

*   **`config/`**: **(Category-centric)** Contains all reusable YAML configuration files. These are named by `category` (e.g., `peaks_model.yml`).
*   **`models/`**: **(Category-centric)** Stores the final trained `.joblib` model artifacts, which are also named by `category`.
*   **`data/`**: **(Segment-centric)** Holds all data files, which are almost always specific to a `segment`.
  *   `data/raw/`: Input feature and target files.
  *   `data/interim/`: Intermediate outputs, such as scored files.
*   **`logs/`**: **(Segment-centric)** Contains detailed output and explanation files from specific runs.

#### File Naming Convention

File names are designed to be self-describing:

*   **Configuration Files:** Are always named for the `category` they configure.
  *   `config/peaks_model.yml`
  *   `config/poi_classification.yml`
*   **Data and Log Files:** Must be prefixed with their `segment` and  `category`.
  *   `data/raw/uswest_peaks_features.csv`
  *   `data/interim/yellowstone_poi_score.csv`
  *   `logs/yellowstone_poi_explain.csv`

---

## Weighted Linear Model (WLM)

This suite  provides a `WeightedLinearModel`, a  sci-kit compatible rule-based model. The final score is calculated
as: `score = intercept + Σ(contribution_of_each_feature)`.

The contribution from each feature is determined by its configured mode:

*   **`presence`**: If the feature is present, add the `coefficient` value.
*   **`value`**: Multiply the feature's value by the `coefficient`.
*   **`base_multiplier`**: If the feature is present, multiply the `base_score_column`'s value by the `coefficient`.

For a detailed guide, see the [Weighted Linear Model Readme](docs/weighted_linear_model.md).

---

## Advanced Workflow: Bootstrapping a Model

The suite is uniquely designed to solve the "cold start" problem where no labeled data exists. You can **bootstrap** a powerful supervised model from your own expertise.

1.  **Encode Expertise:** Manually define your heuristic rules in the configuration for the **Weighted Linear Model (WLM)**.
2.  **Generate Weak Labels:** Run the WLM to produce an initial ranked list.
3.  **Curate a Training Set:** Hand-pick a small, diverse subset of these scored items and adjust their scores to create a high-quality "gold" training set.
4.  **Switch to Supervised Learning:** Change a single line in the model configuration (`model: WLM` -> `model: RFR`) and run the `train` and `tune` steps to create a `RandomForestRegressor` that 
learns the nuanced patterns from your curated labels.  All data extraction and cleanup for the WLM model will continue to be used for RFR.

This process combines the best of both worlds: it starts with your domain knowledge and uses machine learning to scale and refine it.
