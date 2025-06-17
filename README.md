LinkedIn Prfile Finder
 ARCHITECTURE
 Five-Stage Modular Pipeline:
 ▪ Multi-Query Generation & Search
 ▪ Result Enrichment via Scraping
 ▪ Text & Image-Based Similarity
 ▪ Composite Scoring & Ranking
 ▪ Confidence Interval prediction using a weighted 
score technique
CANDIDATE PROFILES
 DISCOVERY
 Input: Partial persona data (e.g., name, bio,
 location)
 Query Crafting: 5 context-rich queries per
 persona + “LinkedIn”
 Multi-Engine Search: Google + DuckDuckGo
 Scraping: Headless browser for dynamic content
 Fields Extracted: Name, Title, Experience,
 Education and Profile Photo
 Format: Structured JSON – ready for cross-modal
 comparison
SIMILARITY SCORING
 STRATEGY
 Post-Discovery Step: For each
 persona, multiple candidate
 profiles are fetched
 Step 1 – Image Similarity (CV2 +
 Face Encoding):
    Compute face similarity
 between persona and profile
 image
    ▪ Threshold-based scoring:
         0.9 → +3 score
         0.7 → +2 score
 Step 2 – Textual Overlap-Based
 Scoring:
 n-gram overlap between persona
 bio & profile description
   Unigram match → +1
   Bigram match → +2
   Trigram match → +3
FINAL RANKING
 & SELECTION
 Scoring Breakdown: 
▪ Image Similarity Score (max 3)
 ▪ n-gram Overlap Score (1–3 per match)
 ▪ Name Similarity Match → +1
 ▪ Overal Profile-Persona Similarity → +1
 Image
 Similarity
 N-gram
 Overlap
 Name 
Similarity
 Sequence
 Similarity
 Composite Score Calculation:
 ▪ Al partial scores are summed up
 ▪ Profile with highest total score selected as final match
CI SCORE CALCULATION
 Final confidence score to quantify match reliability (0
100%)
 CI Score = Weighted Composite Score:
 ▪ 35% → Semantic Text Similarity (Sentence-BERT)
 ▪ 30% → Image Similarity (from earlier pipeline stage)
 ▪ 25% → Name Similarity
 ▪ 10% → N-gram Bonus (presence of bigrams/trigrams
 CONCLUSION
 Developed a multi-stage system to match incomplete personas to LinkedIn profiles
 Combined search-based discovery, text + image similarity, and rule-based +
 weighted scoring
 Integrated state-of-the-art NLP (Sentence-BERT) and CV (face matching) models
 Designed an interpretable Confidence Index (CI) Score for ranking result
 Modular pipeline using JSON workflows enables easy debugging, tracking, and
 reuse
 Solution is scalable, explainable, and highly relevant for sales, hiring, and
 networking use cases
 ## Installation Instructions

1. Place the testing file at:
   ```
   dataset/test.json
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   make run
   ```

## Results
The confidence scores will be available at:
```
temp/confidence_scores.csv
```
