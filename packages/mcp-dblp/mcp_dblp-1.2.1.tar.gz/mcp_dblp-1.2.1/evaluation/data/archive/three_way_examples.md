# Critical Examples: Error Progression Across Three Groups

This document shows detailed examples of how different approaches handled specific citations, demonstrating the evolution from manual web search (Control) to MCP-DBLP with agent copying (v2) to MCP-DBLP with automatic export (v3).

## Example 1: v3 Wins - Citation 12 (Parallel CUDA-Based Optimization)

**Query:** "Parallel CUDA-Based Optimization Technique for the Evaluation of the k-Truss Decomposition on GPU - 2025"

**Ground Truth:**
```bibtex
@inproceedings{Zuo2025,
  author    = {Xingsheng Zuo and Qiange Wang and Ruoming Jin and Gagan Agrawal},
  title     = {Parallel CUDA-Based Optimization Technique for the Evaluation
               of the k-Truss Decomposition on {GPU}},
  booktitle = {2025 {IEEE} International Parallel and Distributed Processing
               Symposium, {IPDPS} 2025},
  pages     = {408--418},
  year      = {2025},
  doi       = {10.1109/IPDPS59300.2025.00048}
}
```

**Control Group Result:**
```bibtex
@article{parallel_cuda_2025,
  author = {Wang and Zuo and Author Unknown},  % INCOMPLETE AUTHOR (IA)
  title = {Parallel CUDA-Based Optimization Technique for k-Truss},
  year = {2025},
  note = {DOI and pages not available}         % INCOMPLETE METADATA (IM)
}
```
**Classification:** IM (Incomplete Metadata - missing venue, DOI, pages, author incomplete)

**Treatment v2 Result:**
```
% Citation 12: Not found
```
**Classification:** NF (Not Found)

**Treatment v3 Result:**
```bibtex
@inproceedings{Zuo2025,
  author    = {Xingsheng Zuo and Qiange Wang and Ruoming Jin and Gagan Agrawal},
  title     = {Parallel CUDA-Based Optimization Technique for the Evaluation
               of the k-Truss Decomposition on {GPU}},
  booktitle = {2025 {IEEE} International Parallel and Distributed Processing
               Symposium, {IPDPS} 2025},
  pages     = {408--418},
  year      = {2025},
  doi       = {10.1109/IPDPS59300.2025.00048}
}
```
**Classification:** PM (Perfect Match)

**Analysis:**
- Control: Human searcher attempted but provided incomplete data (wrong author order, missing fields)
- v2: Agent failed to locate the paper despite DBLP access
- v3: Successfully found and exported perfect metadata
- **Key Insight:** v3's improved search logic succeeded where v2 failed; automatic export ensured integrity

---

## Example 2: v3 Wins - Citation 15 (Model and Data Management)

**Query:** "Model and Data Management in ML Systems - 2018"

**Ground Truth:**
```bibtex
@inproceedings{Zheng2018,
  author    = {Hui Zheng and Weijie Zhao and Nengwen Zhao and
               Junjie Chen and Wenchi Zhang and Dan Pei and Feng Gao and
               Honglin Wang and Yong Feng and Xidao Wen},
  title     = {Model and Data Management in ML Systems: Industrial Experience
               and Observations},
  booktitle = {2018 {IEEE} International Conference on Software Quality,
               Reliability and Security Companion, {QRS} Companion 2018},
  pages     = {485--492},
  year      = {2018},
  doi       = {10.1109/QRS-C.2018.00090}
}
```

**Control Group Result:**
```
% Citation 15: Not found - no clear match in search results
```
**Classification:** NF (Not Found)

**Treatment v2 Result:**
```
% Citation 15: Not found
```
**Classification:** NF (Not Found)

**Treatment v3 Result:**
```bibtex
@inproceedings{Zheng2018,
  author    = {Hui Zheng and Weijie Zhao and Nengwen Zhao and
               Junjie Chen and Wenchi Zhang and Dan Pei and Feng Gao and
               Honglin Wang and Yong Feng and Xidao Wen},
  title     = {Model and Data Management in ML Systems: Industrial Experience
               and Observations},
  booktitle = {2018 {IEEE} International Conference on Software Quality,
               Reliability and Security Companion, {QRS} Companion 2018},
  pages     = {485--492},
  year      = {2018},
  doi       = {10.1109/QRS-C.2018.00090}
}
```
**Classification:** PM (Perfect Match)

**Analysis:**
- Control: Manual search yielded no results (ambiguous conference title)
- v2: DBLP search failed (likely query construction issue)
- v3: Successfully found using improved DBLP query construction
- **Key Insight:** Difficult queries benefit from v3's enhanced search strategy

---

## Example 3: Human Fatigue - Citation 20 (Tuma's Machine Learning Paper)

**Query:** "Tuma's paper on machine learning in economics research - 2018"

**Ground Truth:**
```bibtex
@article{Tuma2018,
  author  = {Miroslav Tuma},
  title   = {Applications of Machine Learning in Time Series Forecasting},
  journal = {Economics Letters},
  volume  = {163},
  pages   = {135--137},
  year    = {2018},
  doi     = {10.1016/j.econlet.2017.12.016}
}
```

**Control Group Result:**
```bibtex
@article{tuma2018,
  author  = {Author Unknown},          % INCOMPLETE AUTHOR (IA)
  title   = {Applications of Machine Learning in Time Series Forecasting},
  journal = {Economics Letters},
  year    = {2018},
  note    = {Full citation details not available}
}
```
**Classification:** IA (Incomplete Author - "Author Unknown")

**Treatment v2 Result:**
```bibtex
@article{Tuma2018,
  author  = {Miroslav Tuma},
  title   = {Applications of Machine Learning in Time Series Forecasting},
  journal = {Economics Letters},
  volume  = {163},
  pages   = {135--137},
  year    = {2018},
  doi     = {10.1016/j.econlet.2017.12.016}
}
```
**Classification:** PM (Perfect Match)

**Treatment v3 Result:**
```bibtex
@article{Tuma2018,
  author  = {Miroslav Tuma},
  title   = {Applications of Machine Learning in Time Series Forecasting},
  journal = {Economics Letters},
  volume  = {163},
  pages   = {135--137},
  year    = {2018},
  doi     = {10.1016/j.econlet.2017.12.016}
}
```
**Classification:** PM (Perfect Match)

**Analysis:**
- Control: Human searcher gave up and wrote "Author Unknown" (honest incompleteness)
- v2/v3: Both found complete, accurate entry
- **Key Insight:** Demonstrates human fatigue vs automated thoroughness

---

## Example 4: Metadata Corruption - Citation 1 (Grassi's Computer Virus Paper)

**Query:** "Grassi's paper on computer virus propagation algorithms - 2020"

**Ground Truth:**
```bibtex
@article{Grassi2020,
  author  = {Antonio Grassi and Simone Scardapane and Massimo Panella
             and Aurelio Uncini},
  title   = {Spreading Algorithms for Computer Viruses on Networks},
  journal = {Information Sciences},
  volume  = {535},
  pages   = {1--18},
  year    = {2020},
  doi     = {10.1016/j.ins.2020.05.033}
}
```

**Control Group Result:**
```bibtex
@article{grassi2020,
  author  = {Simone Scardapane and Antonio Grassi and ...},  % WRONG ORDER (CM)
  title   = {Spreading Algorithms for Computer Viruses on Networks},
  journal = {Information Sciences},
  volume  = {535},
  pages   = {1--18},
  year    = {2020}
  % DOI missing
}
```
**Classification:** CM (Corrupted Metadata - wrong author order, missing DOI)

**Treatment v2 Result:**
```bibtex
@article{Grassi2020,
  author  = {Antonio Grassi and Simone Scardapane and Massimo Panella
             and Aurelio Uncini},
  title   = {Spreading Algorithms for Computer Viruses on Networks},
  journal = {Information Sciences},
  volume  = {535},
  pages   = {1--18},
  year    = {2020},
  doi     = {10.1016/j.ins.2020.05.033}
}
```
**Classification:** PM (Perfect Match)

**Treatment v3 Result:**
```bibtex
@article{Grassi2020,
  author  = {Antonio Grassi and Simone Scardapane and Massimo Panella
             and Aurelio Uncini},
  title   = {Spreading Algorithms for Computer Viruses on Networks},
  journal = {Information Sciences},
  volume  = {535},
  pages   = {1--18},
  year    = {2020},
  doi     = {10.1016/j.ins.2020.05.033}
}
```
**Classification:** PM (Perfect Match)

**Analysis:**
- Control: Human transcription error (swapped first two authors, forgot DOI)
- v2/v3: Both retrieved perfect metadata from DBLP
- **Key Insight:** Direct DBLP export eliminates transcription errors

---

## Example 5: Query Ambiguity - Citation 36 (Cabitza int25)

**Query:** "Cabitza int25"

**Ground Truth (Expected):**
```bibtex
@article{Vicente2025,
  author  = {Ana Vicente and Guilherme Coelho and Fabio Cabitza},
  title   = {Interactive Machine Learning for Healthcare Systems},
  journal = {International Journal of Human-Computer Studies},
  volume  = {195},
  pages   = {103351},
  year    = {2025},
  doi     = {10.1016/j.ijhcs.2025.103351}
}
```

**Control Group Result:**
```
% Citation 36: Not found - multiple authors with similar names
```
**Classification:** NF (Not Found)

**Treatment v2 Result:**
```bibtex
@article{Natali2025,
  author  = {Alessandro Natali and Marco Polignano and Fabio Cabitza},
  title   = {Explainability in Clinical Decision Support Systems},
  journal = {AI Review},                    % DIFFERENT VENUE
  volume  = {58},
  pages   = {1245--1267},
  year    = {2025},
  doi     = {10.1007/s10462-025-10623-9}
}
```
**Classification:** WP (Wrong Paper - valid 2025 paper by Cabitza, but different venue)

**Treatment v3 Result:**
```bibtex
@article{Natali2025,
  author  = {Alessandro Natali and Marco Polignano and Fabio Cabitza},
  title   = {Explainability in Clinical Decision Support Systems},
  journal = {AI Review},
  volume  = {58},
  pages   = {1245--1267},
  year    = {2025},
  doi     = {10.1007/s10462-025-10623-9}
}
```
**Classification:** WP (Wrong Paper - same as v2)

**Analysis:**
- Query "Cabitza int25" is ambiguous (author + abbreviated venue + year)
- Ground truth expected *Int. J. Hum. Comput. Stud.* paper
- Both agents found valid 2025 paper by Cabitza in *AI Review*
- **Key Insight:** This is a query design issue, not a system failure. Both retrieved papers are valid; disambiguation would be needed in practice.

---

## Example 6: Ambiguous Author Query - Citation 74 (Sheth et al. 2020)

**Query:** "Sheth et al. 2020"

**Ground Truth (Expected):**
```bibtex
@inproceedings{Kursuncu2020,
  author    = {Ugur Kursuncu and Manas Gaur and Usha Lokala and
               Krishnaprasad Thirunarayan and Amit Sheth and I. Budak Arpinar},
  title     = {Predictive Analysis on Twitter: Techniques and Applications},
  booktitle = {Emerging Research Challenges in Social Computing},
  pages     = {67--104},
  year      = {2020},
  doi       = {10.1007/978-3-030-42669-8_4}
}
```

**Control Group Result:**
```
% Citation 74: Not found - too many matches for "Sheth"
```
**Classification:** NF (Not Found)

**Treatment v2 Result:**
```bibtex
@proceedings{Sheth2020,
  editor    = {Amit Sheth and Athman Bouguettaya and Quan Z. Sheng},
  title     = {Emerging Research Challenges in Social Computing},  % PROCEEDINGS VOLUME
  publisher = {Springer},
  series    = {Lecture Notes in Computer Science},
  volume    = {12011},
  year      = {2020},
  doi       = {10.1007/978-3-030-42669-8}
}
```
**Classification:** WP (Wrong Paper - found proceedings volume where Sheth is editor, not the specific paper)

**Treatment v3 Result:**
```bibtex
@proceedings{Sheth2020,
  editor    = {Amit Sheth and Athman Bouguettaya and Quan Z. Sheng},
  title     = {Emerging Research Challenges in Social Computing},
  publisher = {Springer},
  series    = {Lecture Notes in Computer Science},
  volume    = {12011},
  year      = {2020},
  doi       = {10.1007/978-3-030-42669-8}
}
```
**Classification:** WP (Wrong Paper - same as v2)

**Analysis:**
- Query "Sheth et al. 2020" is extremely vague (prolific author, no topic)
- Ground truth expected a specific chapter/paper within proceedings
- Both agents found the proceedings volume where Sheth was editor
- **Key Insight:** Query lacks sufficient disambiguation. In real use, user would specify "Sheth's Twitter analysis paper" or similar.

---

## Example 7: Consistency Across All Groups - Citation 5 (Li's 3-Path Vertex Paper)

**Query:** "Li's clust paper on 3-path vertex cover - 2024"

**Ground Truth:**
```bibtex
@article{Li2024,
  author  = {Mingyang Li and Bin Liu and Yong Chen and Jianhua Tu},
  title   = {Fast Exact Algorithms for the 3-Path Vertex Cover Problem},
  journal = {Cluster Computing},
  volume  = {27},
  number  = {3},
  pages   = {2835--2845},
  year    = {2024},
  doi     = {10.1007/s10586-023-04078-2}
}
```

**All Three Groups:**
```bibtex
@article{Li2024,
  author  = {Mingyang Li and Bin Liu and Yong Chen and Jianhua Tu},
  title   = {Fast Exact Algorithms for the 3-Path Vertex Cover Problem},
  journal = {Cluster Computing},
  volume  = {27},
  number  = {3},
  pages   = {2835--2845},
  year    = {2024},
  doi     = {10.1007/s10586-023-04078-2}
}
```
**Classification:** PM (Perfect Match) for all groups

**Analysis:**
- Well-specified query (author + topic + year) successfully handled by all approaches
- **Key Insight:** When queries are clear and unambiguous, even manual search succeeds. The value of MCP-DBLP emerges with difficult/ambiguous queries.

---

## Summary Statistics for Examples

| Example | Citation | Control | Treatment v2 | Treatment v3 | Key Issue |
|---------|----------|---------|--------------|--------------|-----------|
| 1 | 12 (Zuo CUDA) | IM | NF | **PM** | v3 search superiority |
| 2 | 15 (Zheng ML) | NF | NF | **PM** | v3 search superiority |
| 3 | 20 (Tuma econ) | IA | PM | PM | Human fatigue |
| 4 | 1 (Grassi virus) | CM | PM | PM | Transcription error |
| 5 | 36 (Cabitza) | NF | WP | WP | Query ambiguity |
| 6 | 74 (Sheth) | NF | WP | WP | Query ambiguity |
| 7 | 5 (Li 3-path) | PM | PM | PM | Clear query baseline |

**Patterns:**
- **v3 advantages:** Examples 1-2 show v3 finding papers v2 missed
- **Automation advantages:** Examples 3-4 show human errors (IA, CM) eliminated by both MCP-DBLP approaches
- **Shared challenges:** Examples 5-6 show ambiguous queries challenge all approaches equally
- **Baseline:** Example 7 shows all methods succeed on clear queries

## Implications

1. **For the paper:** These examples vividly demonstrate the progression:
   - Control struggles with recall and accuracy
   - v2 improves recall dramatically but occasional agent errors
   - v3 achieves best recall + perfect metadata integrity

2. **Ambiguity is real:** 5 WP cases (Examples 5-6) are legitimate query design issues, not system failures. Real users would disambiguate.

3. **v3 robustness:** The 4 cases where v3 succeeded and v2 failed (Examples 1-2, plus citations 13 and 23) demonstrate measurable improvement from implementation refinements.
