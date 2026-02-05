"""
Deep Research v2 - Research Manager
Core orchestration for all agents
Fixed: Removed details parameter from ProgressUpdate to avoid serialization issues
"""

import asyncio
from typing import AsyncGenerator, Optional, List
from datetime import datetime

from agents import Runner, trace, gen_trace_id

from config import (
    ResearchConfig, ResearchDepth, ReportStyle, 
    CitationStyle, OutputLanguage, DEPTH_SEARCH_COUNT
)
from planner_agent import (
    create_planner_agent, WebSearchPlan, WebSearchItem,
    followup_planner_agent, FollowUpSearchPlan
)
from search_agent import search_agent, SearchResult
from fact_checker_agent import fact_checker_agent, FactCheckReport
from writer_agent import create_writer_agent, ReportData
from email_agent import email_agent


class ProgressUpdate:
    """Simple progress update class - no complex types to avoid Gradio serialization issues"""
    __slots__ = ['stage', 'message', 'progress']
    
    def __init__(self, stage: str, message: str, progress: float):
        self.stage = stage
        self.message = message
        self.progress = progress


class ResearchManager:
    """Manages the entire research workflow"""
    
    def __init__(self):
        self.current_progress = 0.0
        self.total_steps = 0
        self.completed_steps = 0
    
    def _calculate_total_steps(self, config: ResearchConfig) -> int:
        """Calculate total steps based on config"""
        steps = 2  # Planning + Writing
        steps += DEPTH_SEARCH_COUNT[config.depth]  # Searches
        if config.enable_two_phase_search:
            steps += 2  # Follow-up planning + potential searches
        if config.enable_fact_check:
            steps += 1
        if config.send_email:
            steps += 1
        return steps
    
    def _update_progress(self, completed: int = None) -> float:
        """Update and return current progress"""
        if completed is not None:
            self.completed_steps = completed
        return min(self.completed_steps / max(self.total_steps, 1), 1.0)
    
    async def run(self, config: ResearchConfig) -> AsyncGenerator:
        """Run the deep research process with progress updates"""
        start_time = datetime.now()
        trace_id = gen_trace_id()
        
        self.total_steps = self._calculate_total_steps(config)
        self.completed_steps = 0
        
        with trace("Research trace", trace_id=trace_id):
            
            yield ProgressUpdate(
                stage="init",
                message="🚀 Starting research...",
                progress=0.0
            )
            
            # Stage 1: Planning
            yield ProgressUpdate(
                stage="planning",
                message="📋 Planning search strategy...",
                progress=self._update_progress()
            )
            
            search_plan = await self._plan_searches(config)
            self.completed_steps += 1
            
            yield ProgressUpdate(
                stage="planning_complete",
                message=f"✅ Planned {len(search_plan.searches)} searches",
                progress=self._update_progress()
            )
            
            # Stage 2: Searching (collect all results)
            search_results = await self._perform_all_searches(search_plan.searches, config)
            
            # Yield progress for searches
            for i, result in enumerate(search_results):
                self.completed_steps += 1
                yield ProgressUpdate(
                    stage="searching",
                    message=f"🔍 Searched ({i+1}/{len(search_results)}): {result.search_query[:40]}...",
                    progress=self._update_progress()
                )
            
            # Stage 2.5: Follow-up searches (if enabled)
            if config.enable_two_phase_search and len(search_results) > 0:
                yield ProgressUpdate(
                    stage="analyzing_gaps",
                    message="🔎 Analyzing information gaps...",
                    progress=self._update_progress()
                )
                
                followup_plan = await self._plan_followup_searches(config.query, search_results)
                self.completed_steps += 1
                
                if followup_plan.needs_followup and len(followup_plan.searches) > 0:
                    yield ProgressUpdate(
                        stage="followup_search",
                        message=f"📎 Running {len(followup_plan.searches)} follow-up searches...",
                        progress=self._update_progress()
                    )
                    
                    self.total_steps += len(followup_plan.searches)
                    
                    followup_results = await self._perform_all_searches(followup_plan.searches, config)
                    
                    for result in followup_results:
                        search_results.append(result)
                        self.completed_steps += 1
                        yield ProgressUpdate(
                            stage="followup_searching",
                            message=f"🔍 Follow-up: {result.search_query[:40]}...",
                            progress=self._update_progress()
                        )
            
            # Stage 3: Fact Checking (if enabled)
            fact_check_report = None
            if config.enable_fact_check:
                yield ProgressUpdate(
                    stage="fact_checking",
                    message="✓ Verifying facts...",
                    progress=self._update_progress()
                )
                
                fact_check_report = await self._fact_check(search_results)
                self.completed_steps += 1
                
                yield ProgressUpdate(
                    stage="fact_check_complete",
                    message=f"✅ Fact check complete (reliability: {fact_check_report.overall_reliability}/10)",
                    progress=self._update_progress()
                )
            
            # Stage 4: Writing Report
            yield ProgressUpdate(
                stage="writing",
                message="✍️ Writing report...",
                progress=self._update_progress()
            )
            
            report = await self._write_report(config, search_results, fact_check_report)
            self.completed_steps += 1
            
            yield ProgressUpdate(
                stage="writing_complete",
                message=f"✅ Report complete ({report.word_count} words)",
                progress=self._update_progress()
            )
            
            # Stage 5: Send Email (if enabled)
            if config.send_email and config.email_address:
                yield ProgressUpdate(
                    stage="sending_email",
                    message="📧 Sending email...",
                    progress=self._update_progress()
                )
                
                await self._send_email(report, config.email_address)
                self.completed_steps += 1
                
                yield ProgressUpdate(
                    stage="email_sent",
                    message="✅ Email sent",
                    progress=self._update_progress()
                )
            
            # Complete
            duration = (datetime.now() - start_time).total_seconds()
            
            yield ProgressUpdate(
                stage="complete",
                message=f"🎉 Research complete! ({duration:.1f}s)",
                progress=1.0
            )
            
            # Yield the final report
            yield report.markdown_report
    
    async def _plan_searches(self, config: ResearchConfig) -> WebSearchPlan:
        """Plan initial searches"""
        planner = create_planner_agent(config.depth, config.language)
        result = await Runner.run(planner, f"Query: {config.query}")
        return result.final_output_as(WebSearchPlan)
    
    async def _plan_followup_searches(
        self, 
        query: str, 
        initial_results: List[SearchResult]
    ) -> FollowUpSearchPlan:
        """Plan follow-up searches based on gaps"""
        summaries = "\n\n".join([
            f"Query: {r.search_query}\nSummary: {r.summary}\nConfidence: {r.confidence}/5"
            for r in initial_results
        ])
        
        input_text = f"""
Original Query: {query}

Initial Search Results:
{summaries}

Analyze for information gaps and determine if follow-up searches are needed.
"""
        result = await Runner.run(followup_planner_agent, input_text)
        return result.final_output_as(FollowUpSearchPlan)
    
    async def _perform_all_searches(
        self, 
        searches: List[WebSearchItem],
        config: ResearchConfig
    ) -> List[SearchResult]:
        """Perform all searches concurrently and return results"""
        tasks = [
            asyncio.create_task(self._single_search(item)) 
            for item in searches
        ]
        
        results = []
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Search failed: {e}")
                continue
        
        return results
    
    async def _single_search(self, item: WebSearchItem) -> Optional[SearchResult]:
        """Perform a single search"""
        input_text = f"Search term: {item.query}\nReason: {item.reason}"
        
        try:
            result = await Runner.run(search_agent, input_text)
            search_result = result.final_output_as(SearchResult)
            if not search_result.search_query:
                search_result.search_query = item.query
            return search_result
        except Exception as e:
            print(f"Search error for '{item.query}': {e}")
            return None
    
    async def _fact_check(self, search_results: List[SearchResult]) -> FactCheckReport:
        """Fact check the search results"""
        claims = []
        for r in search_results:
            claims.extend(r.key_facts)
        
        input_text = f"""
Please fact-check the following claims from our research:

Key Facts to Verify:
{chr(10).join(f'- {fact}' for fact in claims[:20])}

Search Result Summaries:
{chr(10).join(r.summary for r in search_results)}
"""
        result = await Runner.run(fact_checker_agent, input_text)
        return result.final_output_as(FactCheckReport)
    
    async def _write_report(
        self, 
        config: ResearchConfig,
        search_results: List[SearchResult],
        fact_check: Optional[FactCheckReport]
    ) -> ReportData:
        """Write the final report"""
        writer = create_writer_agent(
            style=config.style,
            citation_style=config.citation_style,
            language=config.language,
            has_fact_check=fact_check is not None
        )
        
        search_summaries = []
        for r in search_results:
            sources_info = ", ".join([
                f"{s.name} ({s.source_type}, {s.credibility_score}/5)" 
                for s in r.sources[:3]
            ])
            search_summaries.append(f"""
Query: {r.search_query}
Summary: {r.summary}
Key Facts: {'; '.join(r.key_facts)}
Sources: {sources_info}
Confidence: {r.confidence}/5
{f'Conflicts: {r.conflicts}' if r.conflicts else ''}
""")
        
        fact_check_info = ""
        if fact_check:
            fact_check_info = f"""

Fact Check Results:
Overall Reliability: {fact_check.overall_reliability}/10
Major Concerns: {'; '.join(fact_check.major_concerns) if fact_check.major_concerns else 'None'}
Summary: {fact_check.summary}
"""
        
        input_text = f"""
Original Query: {config.query}

Search Results:
{'---'.join(search_summaries)}
{fact_check_info}

Please write a comprehensive report following the specified style and format.
"""
        result = await Runner.run(writer, input_text)
        return result.final_output_as(ReportData)
    
    async def _send_email(self, report: ReportData, email_address: str) -> None:
        """Send the report via email"""
        input_text = f"""
Please format and send this report to {email_address}:

{report.markdown_report}

Key Findings:
{chr(10).join(f'- {f}' for f in report.key_findings)}

Follow-up Questions:
{chr(10).join(f'- {q}' for q in report.follow_up_questions)}
"""
        await Runner.run(email_agent, input_text)
