#!/usr/bin/env python3
"""
Database Seed Script - Create Research Dataset

Populates the database with comprehensive test data including:
- Organizations (tech companies, research labs, universities)
- Series (annual reports, video series)
- Resources (reports, videos, tools)
- Collections (curated lists)
- Taxonomy (tags, industries, focus areas)

Usage:
    python3 seed_database.py [--clear]

Options:
    --clear    Clear existing data before seeding
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
import argparse
import random

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


class DatabaseSeeder:
    def __init__(self, clear=False):
        self.clear = clear
        self.conn = psycopg2.connect(DATABASE_URL)
        self.created = {
            'organizations': 0,
            'series': 0,
            'resources': 0,
            'sections': 0,
            'collections': 0,
            'tags': 0,
            'industries': 0,
            'focus_areas': 0
        }

        # Store IDs for relationships
        self.org_ids = {}
        self.series_ids = {}
        self.resource_ids = []

    def log(self, message, level='INFO'):
        """Log progress"""
        prefix = {'INFO': '✓', 'WARN': '⚠', 'ERROR': '✗'}.get(level, '•')
        print(f"{prefix} {message}")

    def clear_database(self):
        """Clear all data (keeps schema)"""
        if not self.clear:
            return

        self.log("Clearing existing data...", 'WARN')
        cursor = self.conn.cursor()

        tables = [
            'collection_item', 'collection', 'section', 'resource',
            'series', 'organization', 'tag', 'industry', 'focus_area'
        ]

        for table in tables:
            try:
                cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
                self.log(f"Cleared {table}", 'INFO')
            except Exception as e:
                self.log(f"Could not clear {table}: {e}", 'WARN')

        self.conn.commit()
        cursor.close()

    def seed_organizations(self):
        """Create sample organizations"""
        self.log("\n=== Creating Organizations ===", 'INFO')

        organizations = [
            {
                'name': 'OpenAI',
                'slug': 'openai',
                'type': 'Company',
                'description': 'AI research and deployment company focused on ensuring artificial general intelligence benefits all of humanity.',
                'website_url': 'https://openai.com',
                'country': 'USA',
                'founded': 2015
            },
            {
                'name': 'Google DeepMind',
                'slug': 'google-deepmind',
                'type': 'Research Lab',
                'description': 'AI research lab combining Google Brain and DeepMind, pushing boundaries of AI capabilities.',
                'website_url': 'https://deepmind.google',
                'country': 'UK',
                'founded': 2010
            },
            {
                'name': 'McKinsey & Company',
                'slug': 'mckinsey',
                'type': 'Company',
                'description': 'Global management consulting firm providing strategic insights on AI and digital transformation.',
                'website_url': 'https://www.mckinsey.com',
                'country': 'USA',
                'founded': 1926
            },
            {
                'name': 'Stanford University',
                'slug': 'stanford-university',
                'type': 'University',
                'description': 'Leading research university with world-class AI programs and the Stanford AI Lab (SAIL).',
                'website_url': 'https://ai.stanford.edu',
                'country': 'USA',
                'founded': 1891
            },
            {
                'name': 'MIT',
                'slug': 'mit',
                'type': 'University',
                'description': 'Massachusetts Institute of Technology, home to cutting-edge AI research and CSAIL.',
                'website_url': 'https://www.csail.mit.edu',
                'country': 'USA',
                'founded': 1861
            },
            {
                'name': 'Anthropic',
                'slug': 'anthropic',
                'type': 'Company',
                'description': 'AI safety company building reliable, interpretable, and steerable AI systems.',
                'website_url': 'https://anthropic.com',
                'country': 'USA',
                'founded': 2021
            },
            {
                'name': 'IBM Research',
                'slug': 'ibm-research',
                'type': 'Research Lab',
                'description': 'IBM\'s global research organization advancing AI, quantum computing, and hybrid cloud.',
                'website_url': 'https://research.ibm.com',
                'country': 'USA',
                'founded': 1945
            },
            {
                'name': 'Meta AI',
                'slug': 'meta-ai',
                'type': 'Research Lab',
                'description': 'Meta\'s AI research division working on computer vision, NLP, and open-source AI.',
                'website_url': 'https://ai.meta.com',
                'country': 'USA',
                'founded': 2013
            },
            {
                'name': 'Hugging Face',
                'slug': 'hugging-face',
                'type': 'Company',
                'description': 'Platform for building, training and deploying machine learning models.',
                'website_url': 'https://huggingface.co',
                'country': 'USA',
                'founded': 2016
            },
            {
                'name': 'AI Index (Stanford HAI)',
                'slug': 'ai-index',
                'type': 'Research Institute',
                'description': 'Stanford\'s initiative tracking AI progress, measuring and analyzing AI trends.',
                'website_url': 'https://aiindex.stanford.edu',
                'country': 'USA',
                'founded': 2017
            }
        ]

        cursor = self.conn.cursor()

        for org in organizations:
            try:
                cursor.execute("""
                    INSERT INTO organization (
                        uuid, name, slug, type, description, website_url,
                        country, founded, created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                    )
                    RETURNING id
                """, (
                    org['name'], org['slug'], org['type'], org['description'],
                    org['website_url'], org['country'], org['founded']
                ))

                org_id = cursor.fetchone()[0]
                self.org_ids[org['slug']] = org_id
                self.created['organizations'] += 1
                self.log(f"Created organization: {org['name']}", 'INFO')

            except Exception as e:
                self.log(f"Error creating {org['name']}: {e}", 'ERROR')

        self.conn.commit()
        cursor.close()

    def seed_series(self):
        """Create sample series"""
        self.log("\n=== Creating Series ===", 'INFO')

        series_data = [
            {
                'name': 'AI Index Report',
                'slug': 'ai-index-report',
                'series_type': 'ANNUAL_REPORT',
                'organization': 'ai-index',
                'description': 'Annual report tracking AI progress, measuring trends in research, development, and adoption.',
                'start_year': 2017,
                'frequency': 'Annual',
                'tags': ['AI trends', 'Research analysis', 'Statistics'],
                'industries': ['Technology', 'Research'],
                'focus_areas': ['AI Progress', 'Market Analysis']
            },
            {
                'name': 'McKinsey Global AI Survey',
                'slug': 'mckinsey-ai-survey',
                'series_type': 'ANNUAL_REPORT',
                'organization': 'mckinsey',
                'description': 'Annual survey of global executives on AI adoption, challenges, and business impact.',
                'start_year': 2017,
                'frequency': 'Annual',
                'tags': ['Enterprise AI', 'Adoption', 'Business Strategy'],
                'industries': ['Consulting', 'Technology', 'Finance'],
                'focus_areas': ['AI Adoption', 'Business Transformation']
            },
            {
                'name': 'DeepMind Research Papers',
                'slug': 'deepmind-research',
                'series_type': 'BLOG_SERIES',
                'organization': 'google-deepmind',
                'description': 'Groundbreaking research from DeepMind on reinforcement learning, protein folding, and more.',
                'start_year': 2016,
                'frequency': 'Ongoing',
                'tags': ['Research', 'Deep Learning', 'Reinforcement Learning'],
                'industries': ['Research', 'Technology'],
                'focus_areas': ['AI Research', 'Scientific Discovery']
            },
            {
                'name': 'Lex Fridman Podcast',
                'slug': 'lex-fridman-podcast',
                'series_type': 'VIDEO_SERIES',
                'organization': 'mit',
                'description': 'Conversations about AI, science, technology, and the human mind.',
                'start_year': 2018,
                'frequency': 'Weekly',
                'tags': ['Podcast', 'Interviews', 'AI Philosophy'],
                'industries': ['Education', 'Media'],
                'focus_areas': ['AI Ethics', 'Philosophy', 'Technology']
            }
        ]

        cursor = self.conn.cursor()

        for series in series_data:
            try:
                org_id = self.org_ids.get(series['organization'])
                if not org_id:
                    self.log(f"Skipping series {series['name']}: org not found", 'WARN')
                    continue

                cursor.execute("""
                    INSERT INTO series (
                        uuid, name, slug, series_type, organization_id,
                        description, start_year, frequency, status,
                        tags, industries, focus_areas,
                        created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, 'PUBLISHED',
                        %s, %s, %s, NOW(), NOW()
                    )
                    RETURNING id
                """, (
                    series['name'], series['slug'], series['series_type'], org_id,
                    series['description'], series['start_year'], series['frequency'],
                    series['tags'], series['industries'], series['focus_areas']
                ))

                series_id = cursor.fetchone()[0]
                self.series_ids[series['slug']] = series_id
                self.created['series'] += 1
                self.log(f"Created series: {series['name']}", 'INFO')

            except Exception as e:
                self.log(f"Error creating series {series['name']}: {e}", 'ERROR')

        self.conn.commit()
        cursor.close()

    def seed_resources(self):
        """Create sample resources"""
        self.log("\n=== Creating Resources ===", 'INFO')

        cursor = self.conn.cursor()

        # AI Index Report editions
        ai_index_id = self.series_ids.get('ai-index-report')
        if ai_index_id:
            for year in [2024, 2023, 2022, 2021]:
                try:
                    cursor.execute("""
                        INSERT INTO resource (
                            uuid, resource_type, name, slug,
                            organization_id, series_id, year, is_latest_edition,
                            short_description, long_description,
                            pdf_urls, thumbnail_urls,
                            primary_url, download_url,
                            publication_date, page_count, language,
                            tags, industries, focus_areas,
                            status, featured, view_count, download_count,
                            created_at, updated_at, published_at
                        ) VALUES (
                            gen_random_uuid(), 'REPORT', %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, 'en',
                            %s, %s, %s, 'PUBLISHED', %s, %s, %s,
                            NOW(), NOW(), NOW()
                        )
                        RETURNING id
                    """, (
                        f"AI Index Report {year}",
                        f"ai-index-report-{year}",
                        self.org_ids['ai-index'],
                        ai_index_id,
                        year,
                        year == 2024,  # is_latest
                        f"Comprehensive report tracking AI progress and trends in {year}",
                        f"The {year} AI Index Report provides a comprehensive overview of AI progress globally, including research output, industry adoption, ethics considerations, and policy developments. The report aggregates data from multiple sources to paint a complete picture of where AI stands.",
                        [f"https://s3.anlak.es/ai-resources/reports/pdf/ai-index-{year}.pdf"],
                        [f"https://s3.anlak.es/ai-resources/reports/thumbnails/ai-index-{year}.png"],
                        f"https://aiindex.stanford.edu/{year}",
                        f"https://aiindex.stanford.edu/wp-content/uploads/{year}/AI-Index-Report_{year}.pdf",
                        f"{year}-03-15",
                        random.randint(200, 400),
                        ['AI trends', 'Research', 'Statistics', 'Global AI'],
                        ['Technology', 'Research', 'Policy'],
                        ['AI Progress', 'Market Analysis', 'Research Trends'],
                        year == 2024,  # featured
                        random.randint(500, 5000),
                        random.randint(100, 1000)
                    ))

                    resource_id = cursor.fetchone()[0]
                    self.resource_ids.append(resource_id)
                    self.created['resources'] += 1
                    self.log(f"Created resource: AI Index Report {year}", 'INFO')

                except Exception as e:
                    self.log(f"Error creating AI Index {year}: {e}", 'ERROR')

        # McKinsey Survey editions
        mckinsey_id = self.series_ids.get('mckinsey-ai-survey')
        if mckinsey_id:
            for year in [2024, 2023, 2022]:
                try:
                    cursor.execute("""
                        INSERT INTO resource (
                            uuid, resource_type, name, slug,
                            organization_id, series_id, year, is_latest_edition,
                            short_description, long_description,
                            pdf_urls, thumbnail_urls,
                            primary_url,
                            publication_date, page_count, language,
                            tags, industries, focus_areas,
                            key_findings, statistics,
                            status, featured, view_count, download_count,
                            created_at, updated_at, published_at
                        ) VALUES (
                            gen_random_uuid(), 'REPORT', %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, 'en',
                            %s, %s, %s, %s, %s,
                            'PUBLISHED', %s, %s, %s,
                            NOW(), NOW(), NOW()
                        )
                        RETURNING id
                    """, (
                        f"McKinsey Global AI Survey {year}",
                        f"mckinsey-ai-survey-{year}",
                        self.org_ids['mckinsey'],
                        mckinsey_id,
                        year,
                        year == 2024,
                        f"Survey of {year} executives on AI adoption and business impact",
                        f"McKinsey's {year} survey reveals how organizations are adopting AI, the challenges they face, and the business value they're achieving. Based on responses from executives across industries globally.",
                        [f"https://s3.anlak.es/ai-resources/reports/pdf/mckinsey-ai-{year}.pdf"],
                        [f"https://s3.anlak.es/ai-resources/reports/thumbnails/mckinsey-ai-{year}.png"],
                        f"https://www.mckinsey.com/capabilities/quantumblack/our-insights/ai-survey-{year}",
                        f"{year}-06-01",
                        random.randint(30, 60),
                        ['Enterprise AI', 'Adoption', 'Business Value', 'ROI'],
                        ['Consulting', 'Finance', 'Technology', 'Healthcare'],
                        ['AI Adoption', 'Business Strategy', 'Digital Transformation'],
                        json.dumps({
                            'respondents': f"{random.randint(800, 1200)}+ global executives",
                            'key_insights': [
                                f"{random.randint(40, 60)}% of organizations have adopted AI in at least one function",
                                'Skills gap remains top barrier to adoption',
                                f"Companies seeing {random.randint(10, 30)}% cost reduction with AI"
                            ]
                        }),
                        json.dumps({
                            'survey_size': random.randint(800, 1200),
                            'countries': random.randint(20, 40),
                            'year_published': year
                        }),
                        year == 2024,
                        random.randint(1000, 8000),
                        random.randint(200, 1500)
                    ))

                    resource_id = cursor.fetchone()[0]
                    self.resource_ids.append(resource_id)
                    self.created['resources'] += 1
                    self.log(f"Created resource: McKinsey Survey {year}", 'INFO')

                except Exception as e:
                    self.log(f"Error creating McKinsey {year}: {e}", 'ERROR')

        # Standalone resources (not part of series)
        standalone_resources = [
            {
                'name': 'Attention Is All You Need',
                'slug': 'attention-is-all-you-need',
                'type': 'REPORT',
                'organization': 'google-deepmind',
                'short_desc': 'Landmark paper introducing the Transformer architecture',
                'long_desc': 'This groundbreaking paper introduced the Transformer model, revolutionizing natural language processing and becoming the foundation for models like GPT and BERT.',
                'authors': ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar', 'Jakob Uszkoreit'],
                'arxiv_id': '1706.03762',
                'doi': '10.48550/arXiv.1706.03762',
                'year': 2017,
                'citations': 92000,
                'tags': ['Transformers', 'NLP', 'Deep Learning', 'Architecture'],
                'primary_url': 'https://arxiv.org/abs/1706.03762'
            },
            {
                'name': 'GPT-4 Technical Report',
                'slug': 'gpt-4-technical-report',
                'type': 'REPORT',
                'organization': 'openai',
                'short_desc': 'Technical report on GPT-4, a large multimodal language model',
                'long_desc': 'OpenAI\'s technical report detailing GPT-4\'s capabilities, training methodology, and safety considerations. GPT-4 exhibits human-level performance on various professional and academic benchmarks.',
                'authors': ['OpenAI'],
                'arxiv_id': '2303.08774',
                'year': 2023,
                'citations': 5000,
                'tags': ['GPT-4', 'Large Language Models', 'Multimodal AI'],
                'primary_url': 'https://arxiv.org/abs/2303.08774',
                'featured': True
            },
            {
                'name': 'Hugging Face Transformers Library',
                'slug': 'huggingface-transformers',
                'type': 'TOOL',
                'organization': 'hugging-face',
                'short_desc': 'State-of-the-art machine learning library for NLP',
                'long_desc': 'Open-source library providing thousands of pretrained models for tasks like text classification, information extraction, question answering, and more.',
                'tool_type': 'Library',
                'license': 'Apache 2.0',
                'language': 'Python',
                'tags': ['NLP', 'Transformers', 'Open Source', 'Python'],
                'primary_url': 'https://huggingface.co/docs/transformers',
                'github_url': 'https://github.com/huggingface/transformers',
                'featured': True
            },
            {
                'name': 'AlphaFold: Protein Structure Prediction',
                'slug': 'alphafold',
                'type': 'TOOL',
                'organization': 'google-deepmind',
                'short_desc': 'AI system for predicting 3D protein structures',
                'long_desc': 'DeepMind\'s AlphaFold revolutionized biology by predicting protein structures with unprecedented accuracy, solving a 50-year-old grand challenge.',
                'tool_type': 'Model',
                'license': 'Apache 2.0',
                'tags': ['Protein Folding', 'Biology', 'Scientific AI', 'Breakthrough'],
                'primary_url': 'https://alphafold.ebi.ac.uk',
                'github_url': 'https://github.com/deepmind/alphafold',
                'featured': True
            }
        ]

        for resource in standalone_resources:
            try:
                org_id = self.org_ids.get(resource['organization'])
                if not org_id:
                    continue

                cursor.execute("""
                    INSERT INTO resource (
                        uuid, resource_type, name, slug,
                        organization_id, series_id,
                        short_description, long_description,
                        primary_url, github_url, download_url,
                        language, license, tool_type,
                        authors, citations, doi, arxiv_id,
                        tags, industries, focus_areas,
                        status, featured, view_count, download_count,
                        created_at, updated_at, published_at
                    ) VALUES (
                        gen_random_uuid(), %s, %s, %s, %s, NULL,
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s,
                        'PUBLISHED', %s, %s, %s,
                        NOW(), NOW(), NOW()
                    )
                    RETURNING id
                """, (
                    resource['type'],
                    resource['name'],
                    resource['slug'],
                    org_id,
                    resource['short_desc'],
                    resource['long_desc'],
                    resource.get('primary_url'),
                    resource.get('github_url'),
                    resource.get('download_url'),
                    resource.get('language'),
                    resource.get('license'),
                    resource.get('tool_type'),
                    resource.get('authors', []),
                    resource.get('citations'),
                    resource.get('doi'),
                    resource.get('arxiv_id'),
                    resource['tags'],
                    resource.get('industries', ['Technology', 'Research']),
                    resource.get('focus_areas', ['AI Research']),
                    resource.get('featured', False),
                    random.randint(1000, 10000),
                    random.randint(500, 5000)
                ))

                resource_id = cursor.fetchone()[0]
                self.resource_ids.append(resource_id)
                self.created['resources'] += 1
                self.log(f"Created resource: {resource['name']}", 'INFO')

            except Exception as e:
                self.log(f"Error creating {resource['name']}: {e}", 'ERROR')

        self.conn.commit()
        cursor.close()

    def seed_collections(self):
        """Create sample collections"""
        self.log("\n=== Creating Collections ===", 'INFO')

        if len(self.resource_ids) < 3:
            self.log("Not enough resources for collections", 'WARN')
            return

        cursor = self.conn.cursor()

        collections = [
            {
                'name': 'Essential AI Papers 2023',
                'slug': 'essential-ai-papers-2023',
                'description': 'Must-read AI research papers from 2023',
                'curator_name': 'AI Research Team'
            },
            {
                'name': 'Enterprise AI Adoption Guides',
                'slug': 'enterprise-ai-guides',
                'description': 'Resources for business leaders implementing AI',
                'curator_name': 'Business Strategy Team'
            }
        ]

        for coll in collections:
            try:
                cursor.execute("""
                    INSERT INTO collection (
                        uuid, name, slug, description, curator_name,
                        status, featured, created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), %s, %s, %s, %s, 'PUBLISHED', true, NOW(), NOW()
                    )
                    RETURNING id
                """, (coll['name'], coll['slug'], coll['description'], coll['curator_name']))

                collection_id = cursor.fetchone()[0]

                # Add random resources to collection
                selected_resources = random.sample(self.resource_ids, min(3, len(self.resource_ids)))
                for i, resource_id in enumerate(selected_resources):
                    cursor.execute("""
                        INSERT INTO collection_item (
                            collection_id, resource_id, "order", note, added_at
                        ) VALUES (%s, %s, %s, %s, NOW())
                    """, (collection_id, resource_id, i + 1, f"Essential reading #{i + 1}"))

                self.created['collections'] += 1
                self.log(f"Created collection: {coll['name']}", 'INFO')

            except Exception as e:
                self.log(f"Error creating collection {coll['name']}: {e}", 'ERROR')

        self.conn.commit()
        cursor.close()

    def seed_taxonomy(self):
        """Create taxonomy entries"""
        self.log("\n=== Creating Taxonomy ===", 'INFO')

        cursor = self.conn.cursor()

        # Tags
        tags = [
            ('AI Ethics', 'ai-ethics', 'topic'),
            ('Machine Learning', 'machine-learning', 'technology'),
            ('Deep Learning', 'deep-learning', 'technology'),
            ('NLP', 'nlp', 'technology'),
            ('Computer Vision', 'computer-vision', 'technology'),
            ('Enterprise AI', 'enterprise-ai', 'industry'),
            ('Research', 'research', 'topic')
        ]

        for name, slug, category in tags:
            try:
                cursor.execute("""
                    INSERT INTO tag (name, slug, category, created_at)
                    VALUES (%s, %s, %s, NOW())
                """, (name, slug, category))
                self.created['tags'] += 1
            except Exception as e:
                pass  # Ignore duplicates

        # Industries
        industries = [
            ('Technology', 'technology'),
            ('Healthcare', 'healthcare'),
            ('Finance', 'finance'),
            ('Education', 'education'),
            ('Research', 'research'),
            ('Consulting', 'consulting')
        ]

        for name, slug in industries:
            try:
                cursor.execute("""
                    INSERT INTO industry (name, slug, created_at)
                    VALUES (%s, %s, NOW())
                """, (name, slug))
                self.created['industries'] += 1
            except:
                pass

        # Focus Areas
        focus_areas = [
            ('AI Research', 'ai-research', '#667eea'),
            ('Business Strategy', 'business-strategy', '#f093fb'),
            ('AI Ethics', 'ai-ethics', '#4ecdc4'),
            ('Technical Implementation', 'technical-implementation', '#ff6b6b')
        ]

        for name, slug, color in focus_areas:
            try:
                cursor.execute("""
                    INSERT INTO focus_area (name, slug, color, created_at)
                    VALUES (%s, %s, %s, NOW())
                """, (name, slug, color))
                self.created['focus_areas'] += 1
            except:
                pass

        self.conn.commit()
        cursor.close()

    def print_summary(self):
        """Print seeding summary"""
        self.log("\n" + "=" * 60, 'INFO')
        self.log("DATABASE SEEDING COMPLETE", 'INFO')
        self.log("=" * 60, 'INFO')
        for key, count in self.created.items():
            self.log(f"{key.replace('_', ' ').title()}: {count}", 'INFO')
        self.log("=" * 60, 'INFO')

    def run(self):
        """Run complete seeding"""
        try:
            self.log("=" * 60, 'INFO')
            self.log("AI RESOURCES DATABASE SEEDING", 'INFO')
            self.log("=" * 60, 'INFO')

            self.clear_database()
            self.seed_organizations()
            self.seed_series()
            self.seed_resources()
            self.seed_collections()
            self.seed_taxonomy()
            self.print_summary()

        except Exception as e:
            self.log(f"\nFATAL ERROR: {e}", 'ERROR')
            import traceback
            traceback.print_exc()
        finally:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(description='Seed AI Resources database with test data')
    parser.add_argument('--clear', action='store_true', help='Clear existing data before seeding')

    args = parser.parse_args()

    if args.clear:
        confirm = input("⚠️  This will DELETE all existing data. Are you sure? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return

    seeder = DatabaseSeeder(clear=args.clear)
    seeder.run()


if __name__ == '__main__':
    main()
