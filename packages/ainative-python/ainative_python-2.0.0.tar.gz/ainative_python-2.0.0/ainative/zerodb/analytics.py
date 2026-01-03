"""
ZeroDB Analytics Module

Provides analytics and insights for ZeroDB operations.
"""

from typing import TYPE_CHECKING, Dict, Any, Optional, List
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from ..client import AINativeClient


class AnalyticsClient:
    """Client for ZeroDB analytics operations."""
    
    def __init__(self, client: "AINativeClient"):
        """
        Initialize analytics client.
        
        Args:
            client: Parent AINative client instance
        """
        self.client = client
        self.base_path = "/zerodb/analytics"
    
    def get_usage(
        self,
        project_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        granularity: str = "daily",
    ) -> Dict[str, Any]:
        """
        Get usage analytics.
        
        Args:
            project_id: Optional project ID filter
            start_date: Start date for analytics
            end_date: End date for analytics
            granularity: Data granularity (hourly, daily, weekly, monthly)
        
        Returns:
            Usage analytics data
        """
        params = {"granularity": granularity}
        
        if project_id:
            params["project_id"] = project_id
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        
        return self.client.get(f"{self.base_path}/usage", params=params)
    
    def get_performance_metrics(
        self,
        project_id: Optional[str] = None,
        metric_type: str = "all",
    ) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Args:
            project_id: Optional project ID filter
            metric_type: Type of metrics (latency, throughput, errors, all)
        
        Returns:
            Performance metrics data
        """
        params = {"metric_type": metric_type}
        
        if project_id:
            params["project_id"] = project_id
        
        return self.client.get(f"{self.base_path}/performance", params=params)
    
    def get_storage_stats(
        self,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Args:
            project_id: Optional project ID filter
        
        Returns:
            Storage statistics including size, vector count, etc.
        """
        params = {}
        if project_id:
            params["project_id"] = project_id
        
        return self.client.get(f"{self.base_path}/storage", params=params)
    
    def get_query_insights(
        self,
        project_id: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Get query pattern insights.
        
        Args:
            project_id: Optional project ID filter
            limit: Maximum number of insights
        
        Returns:
            Query insights and patterns
        """
        params = {"limit": limit}
        
        if project_id:
            params["project_id"] = project_id
        
        return self.client.get(f"{self.base_path}/queries", params=params)
    
    def get_cost_analysis(
        self,
        project_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get cost analysis and projections.
        
        Args:
            project_id: Optional project ID filter
            start_date: Start date for analysis
            end_date: End date for analysis
        
        Returns:
            Cost analysis data
        """
        params = {}
        
        if project_id:
            params["project_id"] = project_id
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        
        return self.client.get(f"{self.base_path}/costs", params=params)
    
    def get_trends(
        self,
        metric: str,
        project_id: Optional[str] = None,
        period: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Get trend data for specific metrics.
        
        Args:
            metric: Metric name (vectors, queries, storage, errors)
            project_id: Optional project ID filter
            period: Number of days to analyze
        
        Returns:
            Trend data points
        """
        params = {
            "metric": metric,
            "period": period,
        }
        
        if project_id:
            params["project_id"] = project_id
        
        response = self.client.get(f"{self.base_path}/trends", params=params)
        return response.get("data", [])
    
    def get_anomalies(
        self,
        project_id: Optional[str] = None,
        severity: str = "all",
    ) -> List[Dict[str, Any]]:
        """
        Get detected anomalies in usage patterns.
        
        Args:
            project_id: Optional project ID filter
            severity: Severity filter (low, medium, high, critical, all)
        
        Returns:
            List of detected anomalies
        """
        params = {"severity": severity}
        
        if project_id:
            params["project_id"] = project_id
        
        response = self.client.get(f"{self.base_path}/anomalies", params=params)
        return response.get("anomalies", [])
    
    def export_report(
        self,
        report_type: str = "summary",
        project_id: Optional[str] = None,
        format: str = "json",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Export analytics report.
        
        Args:
            report_type: Type of report (summary, detailed, custom)
            project_id: Optional project ID filter
            format: Export format (json, csv, pdf)
            start_date: Start date for report
            end_date: End date for report
        
        Returns:
            Report data or download URL
        """
        data = {
            "report_type": report_type,
            "format": format,
        }
        
        if project_id:
            data["project_id"] = project_id
        if start_date:
            data["start_date"] = start_date.isoformat()
        if end_date:
            data["end_date"] = end_date.isoformat()
        
        return self.client.post(f"{self.base_path}/export", data=data)