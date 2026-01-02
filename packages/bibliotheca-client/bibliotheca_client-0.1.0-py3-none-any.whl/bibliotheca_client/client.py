"""
Bibliotheca Client

HTTP client for interacting with Bibliotheca backend APIs.
"""

import requests
import json
from typing import List, Dict, Any, Optional, Literal
import pandas as pd

try:
    import sqlglot
    SQLGLOT_AVAILABLE = True
except ImportError:
    SQLGLOT_AVAILABLE = False


class BibliothecaClient:
    """
    Client for interacting with the Bibliotheca data exploration platform.
    
    This client communicates with the Bibliotheca backend APIs to generate
    hypotheses and SQL queries for data exploration.
    
    Args:
        base_url (str): Base URL of the Bibliotheca backend API
        id_token (str, optional): Firebase authentication ID token (deprecated, use api_key)
        api_key (str, optional): Bibliotheca API key (recommended for notebooks/scripts)
    
    Example with API Key (recommended):
        >>> client = BibliothecaClient(
        ...     base_url="https://your-backend.run.app",
        ...     api_key="bib_xxxxxxxxxxxxxxxxx"
        ... )
        >>> hypotheses = client.generate_hypotheses("my-database")
    
    Example with Firebase Token:
        >>> client = BibliothecaClient(
        ...     base_url="https://your-backend.run.app",
        ...     id_token="your-firebase-token"
        ... )
    """
    
    def __init__(self, base_url: str, id_token: str = None, api_key: str = None):
        """Initialize the Bibliotheca client.
        
        Args:
            base_url: The base URL of the Bibliotheca backend API (e.g., 'https://api.bibliotheca.com')
            id_token: (Optional) Firebase authentication ID token for API authentication
            api_key: (Optional) Bibliotheca API key (recommended for programmatic access)
        
        Note:
            You must provide either id_token or api_key. API keys are recommended for
            notebook and programmatic usage.
        """
        if not id_token and not api_key:
            raise ValueError("Either id_token or api_key must be provided")
        
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # Use API key if provided, otherwise fall back to id_token
        if api_key:
            self.auth_token = api_key
            self.auth_type = 'api_key'
        else:
            self.auth_token = id_token
            self.auth_type = 'firebase'
        
        self.session.headers.update({
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        })
    
    def create_api_key(self) -> Dict[str, Any]:
        """Create a new API key for your account.
        
        Note: This requires Firebase authentication (id_token).
        You cannot create API keys using an API key.
        
        Returns:
            dict: API key information including the key itself (shown only once)
        
        Example:
            >>> # Must use Firebase token to create API keys
            >>> client = BibliothecaClient(base_url="...", id_token="...")
            >>> result = client.create_api_key()
            >>> print(result['api_key'])  # Save this key - won't be shown again!
        """
        if self.auth_type != 'firebase':
            raise ValueError("Creating API keys requires Firebase authentication (id_token)")
        
        response = self.session.post(f'{self.base_url}/api_keys/create')
        response.raise_for_status()
        
        result = response.json()
        if result['ResponseCode'] != 200:
            raise Exception(result.get('Error', 'Unknown error'))
        
        return result['Data']
    
    def list_api_keys(self) -> List[Dict[str, Any]]:
        """List all API keys for your account.
        
        Returns:
            list: List of API key information (keys are masked for security)
        
        Example:
            >>> keys = client.list_api_keys()
            >>> for key in keys:
            ...     print(f"Key: {key['api_key_masked']}, Tier: {key['tier_name']}")
        """
        response = self.session.get(f'{self.base_url}/api_keys/list')
        response.raise_for_status()
        
        result = response.json()
        if result['ResponseCode'] != 200:
            raise Exception(result.get('Error', 'Unknown error'))
        
        return result['Data']
    
    def revoke_api_key(self, key_id: str) -> Dict[str, Any]:
        """Revoke one of your API keys.
        
        Args:
            key_id: The ID of the API key to revoke
        
        Returns:
            dict: Confirmation message
        
        Example:
            >>> client.revoke_api_key("key-id-here")
        """
        response = self.session.post(
            f'{self.base_url}/api_keys/revoke',
            json={'key_id': key_id}
        )
        response.raise_for_status()
        
        result = response.json()
        if result['ResponseCode'] != 200:
            raise Exception(result.get('Error', 'Unknown error'))
        
        return result['Data']
    
    def get_usage(self) -> Dict[str, Any]:
        """Get token usage information for the current API key.
        
        Note: Only works when authenticated with an API key, not Firebase token.
        
        Returns:
            dict: Usage information including tier, limit, tokens used, etc.
        
        Example:
            >>> usage = client.get_usage()
            >>> print(f"Used {usage['tokens_used_today']} of {usage['daily_limit']} tokens")
            >>> print(f"Tier: {usage['tier_name']}")
        """
        if self.auth_type != 'api_key':
            raise ValueError("Usage information only available for API key authentication")
        
        response = self.session.get(f'{self.base_url}/api_keys/usage')
        response.raise_for_status()
        
        result = response.json()
        if result['ResponseCode'] != 200:
            raise Exception(result.get('Error', 'Unknown error'))
        
        return result['Data']
    
    def generate_hypotheses(
        self,
        user_grouping: str,
        hypothesis_model: str = 'gemini-2.5-pro',
        user_context: str = ""
    ) -> List[Dict[str, str]]:
        """
        Generate data exploration hypotheses based on available database schema.
        
        This method analyzes the database schema and returns three testable hypotheses
        that users can explore through SQL queries.
        
        Args:
            user_grouping: Database grouping identifier (from your data source configuration)
            hypothesis_model: LLM model to use for hypothesis generation (default: 'gemini-2.5-pro')
            user_context: Optional context about what you want to explore
        
        Returns:
            List of hypothesis dictionaries, each containing:
                - title: Short hypothesis title
                - description: Detailed description
                - question: Exploratory question to investigate
        
        Raises:
            requests.HTTPError: If the API request fails
            ValueError: If the response format is invalid
        
        Example:
            >>> hypotheses = client.generate_hypotheses(
            ...     user_grouping="sales-analytics",
            ...     user_context="I want to understand customer purchase patterns"
            ... )
            >>> for h in hypotheses:
            ...     print(f"{h['title']}: {h['question']}")
        """
        url = f"{self.base_url}/generate_hypotheses"
        
        payload = {
            'user_grouping': user_grouping,
            'hypothesis_model': hypothesis_model,
            'user_context': user_context
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('ResponseCode') != 200:
            raise ValueError(f"API returned error: {data.get('Error', 'Unknown error')}")
        
        return data.get('Hypotheses', [])
    
    def generate_sql(
        self,
        session_id: str,
        user_question: str,
        user_grouping: str,
        run_debugger: bool = True,
        debugging_rounds: int = 2,
        llm_validation: bool = False,
        embedder_model: str = 'vertex',
        sqlbuilder_model: str = 'gemini-2.5-pro',
        sqlchecker_model: str = 'gemini-2.5-pro',
        sqldebugger_model: str = 'gemini-2.5-pro',
        num_table_matches: int = 5,
        num_column_matches: int = 10,
        table_similarity_threshold: float = 0.1,
        column_similarity_threshold: float = 0.1,
        example_similarity_threshold: float = 0.1,
        num_sql_matches: int = 3,
        target_dialect: Optional[Literal['spark', 'bigquery', 'postgres', 'mysql', 'snowflake']] = None
    ) -> Dict[str, Any]:
        """
        Generate SQL query from a natural language question.
        
        This method converts a natural language question into an executable SQL query
        by analyzing the database schema and using AI to generate appropriate SQL.
        
        Args:
            session_id: Session identifier for conversation tracking
            user_question: Natural language question to convert to SQL
            user_grouping: Database grouping identifier
            run_debugger: Whether to run SQL validation and debugging
            debugging_rounds: Number of debugging iterations
            llm_validation: Whether to use LLM for SQL validation
            embedder_model: Model for text embedding
            sqlbuilder_model: Model for SQL generation
            sqlchecker_model: Model for SQL validation
            sqldebugger_model: Model for SQL debugging
            num_table_matches: Number of similar tables to retrieve
            num_column_matches: Number of similar columns to retrieve
            table_similarity_threshold: Similarity threshold for table matching
            column_similarity_threshold: Similarity threshold for column matching
            example_similarity_threshold: Similarity threshold for example queries
            target_dialect: Optional SQL dialect to translate to ('spark', 'bigquery', 'postgres', 'mysql', 'snowflake')
                           If specified, the generated SQL will be automatically translated from PostgreSQL to this dialect.
        
        Returns:
            Dictionary containing:
                - ResponseCode: HTTP status code
                - GeneratedSQL: The generated SQL query (translated if target_dialect specified)
                - SessionId: Session identifier for follow-up queries
                - Error: Error message if any
        
        Raises:
            requests.HTTPError: If the API request fails
            ImportError: If sqlglot is not installed and target_dialect is specified
        
        Example:
            >>> # Get SQL in Spark dialect for Databricks
            >>> result = client.generate_sql(
            ...     session_id="my-session-123",
            ...     user_question="What are the top 10 products by revenue?",
            ...     user_grouping="sales-analytics",
            ...     target_dialect='spark'
            ... )
            >>> spark_sql = result['GeneratedSQL']  # Already in Spark SQL!
            >>> results_df = spark.sql(spark_sql).toPandas(
            >>> print(result['GeneratedSQL'])
        """
        url = f"{self.base_url}/generate_sql"
        
        payload = {
            'session_id': session_id,
            'user_question': user_question,
            'user_grouping': user_grouping,
            'run_debugger': run_debugger,
            'debugging_rounds': debugging_rounds,
            'llm_validation': llm_validation,
            'embedder_model': embedder_model,
            'sqlbuilder_model': sqlbuilder_model,
            'sqlchecker_model': sqlchecker_model,
            'sqldebugger_model': sqldebugger_model,
            'num_table_matches': num_table_matches,
            'num_column_matches': num_column_matches,
            'table_similarity_threshold': table_similarity_threshold,
            'column_similarity_threshold': column_similarity_threshold,
            'example_similarity_threshold': example_similarity_threshold,
            'num_sql_matches': num_sql_matches
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # Automatically translate SQL if target_dialect is specified
        if target_dialect and target_dialect != 'postgres' and result.get('ResponseCode') == 200:
            generated_sql = result.get('GeneratedSQL', '')
            if generated_sql:
                try:
                    result['GeneratedSQL'] = self.translate_sql(generated_sql, target_dialect)
                except Exception as e:
                    # Add translation error to response but don't fail
                    result['TranslationWarning'] = f"Failed to translate SQL to {target_dialect}: {str(e)}"
        
        return result
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def get_available_databases(self) -> List[Dict[str, str]]:
        """
        Retrieve list of available databases/groupings.
        
        Returns:
            List of database dictionaries with schema information
        
        Example:
            >>> databases = client.get_available_databases()
            >>> for db in databases:
            ...     print(db['table_schema'])
        """
        url = f"{self.base_url}/available_databases"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('ResponseCode') != 200:
            raise ValueError(f"API returned error: {data.get('Error', 'Unknown error')}")
        
        # Backend returns 'KnownDB' as a JSON string, parse it
        known_db = data.get('KnownDB', '[]')
        if isinstance(known_db, str):
            import json
            return json.loads(known_db)
        return known_db
    
    def translate_sql(
        self,
        sql: str,
        target_dialect: Literal['spark', 'bigquery', 'postgres', 'mysql', 'snowflake'] = 'spark'
    ) -> str:
        """
        Translate SQL from PostgreSQL (backend default) to target dialect.
        
        This method converts the PostgreSQL SQL generated by the backend into
        the dialect used by your database environment (Spark, BigQuery, etc.).
        
        Args:
            sql: The SQL query to translate (typically PostgreSQL from backend)
            target_dialect: Target SQL dialect ('spark', 'bigquery', 'postgres', 'mysql', 'snowflake')
        
        Returns:
            Translated SQL query in the target dialect
        
        Raises:
            ImportError: If sqlglot is not installed
            ValueError: If translation fails
        
        Example:
            >>> # Backend returns PostgreSQL SQL
            >>> pg_sql = result['GeneratedSQL']
            >>> 
            >>> # Translate to Spark SQL for Databricks
            >>> spark_sql = client.translate_sql(pg_sql, target_dialect='spark')
            >>> results_df = spark.sql(spark_sql).toPandas()
        
        Note:
            This requires the `sqlglot` library. Install with:
            pip install sqlglot
        """
        if not SQLGLOT_AVAILABLE:
            raise ImportError(
                "sqlglot is required for SQL translation. "
                "Install it with: pip install sqlglot"
            )
        
        try:
            # Parse PostgreSQL and transpile to target dialect
            translated = sqlglot.transpile(sql, read='postgres', write=target_dialect)[0]
            return translated
        except Exception as e:
            raise ValueError(f"Failed to translate SQL to {target_dialect}: {str(e)}")
    
    def update_token(self, id_token: str):
        """
        Update the authentication token.
        
        Use this method to refresh the Firebase ID token when it expires.
        
        Args:
            id_token: New Firebase authentication ID token
        """
        self.id_token = id_token
        self.session.headers.update({
            'Authorization': f'Bearer {id_token}'
        })
