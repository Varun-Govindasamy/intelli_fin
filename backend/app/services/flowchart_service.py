import os
import json
from typing import Dict, List
import openai
from dotenv import load_dotenv

load_dotenv()

class FlowchartService:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def generate_flowchart(self, financial_goal: str, time_horizon: str, risk_tolerance: str) -> Dict:
        """Generate financial planning flowchart using OpenAI GPT"""
        try:
            # Extract amount from financial goal if present
            amount = self._extract_amount_from_goal(financial_goal)
            
            # Create enhanced prompt for OpenAI with investment allocation focus
            prompt = f"""
            Create a comprehensive financial planning flowchart with detailed investment allocation for:
            
            Financial Goal: {financial_goal}
            Time Horizon: {time_horizon}
            Risk Tolerance: {risk_tolerance}
            
            IMPORTANT: Include a detailed investment allocation plan that:
            
            1. Suggests exact amounts (not percentages) for different investment categories:
               - Fixed Deposit (FD)
               - Recurring Deposit (RD) 
               - Mutual Funds (SIP/Lump sum)
               - Stocks/Equity
               - Gold (physical/digital/ETF)
               - Bonds/Debt funds
               - Liquid funds for emergency
            
            2. Allocation guidelines based on inputs:
               - Short-term (< 1 year): Prioritize FD, liquid funds, short-term debt
               - Medium-term (1-3 years): Balance between FD, debt funds, conservative equity
               - Long-term (> 3 years): Higher equity allocation, SIPs, growth funds
               - Low risk: 70-80% safe instruments (FD/RD/Debt), 20-30% moderate risk
               - Medium risk: 50-60% safe, 40-50% equity/mutual funds
               - High risk: 30-40% safe, 60-70% equity/aggressive funds
            
            3. For each allocation, explain:
               - Why this category was chosen
               - How it helps reach the goal
               - Expected returns/safety level
               - Liquidity considerations
            
            4. Always include emergency fund considerations
            
            5. Give specific rupee amounts for each category
            
            Example format to follow:
            Goal: [Goal name]
            Amount: ₹[Total amount]
            
            Investment Allocation:
            • ₹[Amount] → Fixed Deposit (12 months) – Guaranteed 7-8% returns, completely safe
            • ₹[Amount] → Equity Mutual Fund SIP – Growth potential 12-15%, suits long-term goal
            • ₹[Amount] → Liquid Fund – Emergency buffer, 4-5% returns, instant withdrawal
            
            Reasoning: [Explain why this allocation suits the risk profile and time horizon]
            
            Structure the complete response as a logical 6-8 step flowchart including this allocation detail.
            """
            
            # Generate flowchart structure using OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert financial planner and certified investment advisor specializing in Indian financial markets. 
                        Create detailed, actionable financial flowcharts with specific investment allocations.
                        Always provide exact rupee amounts for each investment category.
                        Consider current Indian market conditions, interest rates, and investment options.
                        Focus on practical, implementable advice with clear reasoning for each allocation."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=3000,
                temperature=0.7
            )
            
            # Parse the response and create flowchart data
            openai_response = response.choices[0].message.content
            
            # Create enhanced flowchart data with investment allocation
            flowchart_data = self._create_enhanced_flowchart_structure(
                financial_goal, time_horizon, risk_tolerance, openai_response, amount
            )
            
            return flowchart_data
            
        except Exception as e:
            print(f"Error generating flowchart: {e}")
            # Return an enhanced basic flowchart structure as fallback
            return self._create_enhanced_basic_flowchart(financial_goal, time_horizon, risk_tolerance)
    
    def _extract_amount_from_goal(self, goal: str) -> str:
        """Extract monetary amount from financial goal"""
        import re
        
        # Look for common currency patterns
        patterns = [
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)',  # ₹10,000 or ₹1,50,000
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:rupees?|rs\.?|₹)',  # 10000 rupees
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lakhs?)',  # 5 lakh
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:crore|crores?)',  # 1 crore
        ]
        
        for pattern in patterns:
            match = re.search(pattern, goal.lower())
            if match:
                amount_str = match.group(1)
                # Convert lakh/crore to actual numbers
                if 'lakh' in goal.lower():
                    amount = float(amount_str.replace(',', '')) * 100000
                    return f"₹{amount:,.0f}"
                elif 'crore' in goal.lower():
                    amount = float(amount_str.replace(',', '')) * 10000000
                    return f"₹{amount:,.0f}"
                else:
                    return f"₹{amount_str}"
        
        # Default amount if none found
        return "₹50,000"
    
    def _create_enhanced_flowchart_structure(self, goal: str, horizon: str, risk: str, openai_response: str, amount: str = None) -> Dict:
        """Create enhanced React Flow compatible flowchart structure"""
        try:
            nodes = []
            edges = []
            
            # Enhanced start node
            nodes.append({
                "id": "start",
                "type": "startNode",
                "position": {"x": 400, "y": 50},
                "data": {
                    "label": "Financial Goal",
                    "description": goal[:100] + "..." if len(goal) > 100 else goal,
                    "icon": "RocketLaunchIcon"
                }
            })
            
            # Parse enhanced steps from OpenAI response
            steps = self._parse_enhanced_steps_from_response(openai_response, horizon, risk)
            
            # Create nodes with better positioning and enhanced data
            positions = self._calculate_enhanced_positions(len(steps))
            
            for i, step in enumerate(steps):
                node_id = f"step_{i+1}"
                position = positions[i]
                
                # Determine node type based on step content
                node_type = self._determine_node_type(step, i, len(steps))
                
                nodes.append({
                    "id": node_id,
                    "type": node_type,
                    "position": position,
                    "data": {
                        "label": step["title"],
                        "description": step["description"],
                        "icon": step.get("icon", "CogIcon"),
                        "timeline": step.get("timeline", ""),
                        "metrics": step.get("metrics", "")
                    }
                })
                
                # Create enhanced edges
                if i == 0:
                    source_id = "start"
                else:
                    source_id = f"step_{i}"
                
                edge_style = self._get_edge_style(step.get("priority", "normal"))
                
                edges.append({
                    "id": f"edge_{i+1}",
                    "source": source_id,
                    "target": node_id,
                    "type": "smoothstep",
                    "animated": True,
                    "style": edge_style
                })
            
            # Enhanced end node
            nodes.append({
                "id": "end",
                "type": "endNode",
                "position": {"x": 400, "y": 200 + len(steps) * 150},
                "data": {
                    "label": "Goal Achieved",
                    "description": f"Successfully completed: {goal[:50]}{'...' if len(goal) > 50 else ''}",
                    "icon": "TrophyIcon"
                }
            })
            
            # Final edge to end
            if steps:
                edges.append({
                    "id": "edge_final",
                    "source": f"step_{len(steps)}",
                    "target": "end",
                    "type": "smoothstep",
                    "animated": True,
                    "style": {
                        "stroke": "#8b5cf6",
                        "strokeWidth": 3,
                        "filter": "drop-shadow(0 2px 4px rgba(139, 92, 246, 0.3))"
                    }
                })
            
            # Add feedback loops for monitoring steps
            self._add_feedback_loops(nodes, edges, steps)
            
            return {
                "nodes": nodes,
                "edges": edges,
                "metadata": {
                    "goal": goal,
                    "time_horizon": horizon,
                    "risk_tolerance": risk,
                    "target_amount": amount or self._extract_amount_from_goal(goal),
                    "generated_plan": openai_response,
                    "step_count": len(steps),
                    "complexity": "enhanced",
                    "investment_allocation": self._extract_investment_allocation(openai_response)
                }
            }
            
        except Exception as e:
            print(f"Error creating enhanced flowchart structure: {e}")
            return self._create_enhanced_basic_flowchart(goal, horizon, risk)
        """Create React Flow compatible flowchart structure"""
        try:
            # Try to extract JSON from LLaMA response
            # If it fails, create a structured flowchart based on the response text
            
            nodes = []
            edges = []
            
            # Start node
            nodes.append({
                "id": "start",
                "type": "input",
                "position": {"x": 250, "y": 0},
                "data": {
                    "label": "Financial Goal",
                    "description": goal
                }
            })
            
            # Parse LLaMA response for steps
            steps = self._parse_steps_from_response(openai_response)
            
            y_position = 100
            for i, step in enumerate(steps):
                node_id = f"step_{i+1}"
                nodes.append({
                    "id": node_id,
                    "type": "default",
                    "position": {"x": 250, "y": y_position},
                    "data": {
                        "label": step["title"],
                        "description": step["description"]
                    }
                })
                
                # Create edge from previous node
                if i == 0:
                    source_id = "start"
                else:
                    source_id = f"step_{i}"
                
                edges.append({
                    "id": f"edge_{i+1}",
                    "source": source_id,
                    "target": node_id,
                    "type": "smoothstep"
                })
                
                y_position += 150
            
            # End node
            nodes.append({
                "id": "end",
                "type": "output",
                "position": {"x": 250, "y": y_position},
                "data": {
                    "label": "Goal Achievement",
                    "description": f"Successfully achieved: {goal}"
                }
            })
            
            # Edge to end
            if steps:
                edges.append({
                    "id": "edge_final",
                    "source": f"step_{len(steps)}",
                    "target": "end",
                    "type": "smoothstep"
                })
            
            return {
                "nodes": nodes,
                "edges": edges,
                "metadata": {
                    "goal": goal,
                    "time_horizon": horizon,
                    "risk_tolerance": risk,
                    "generated_plan": openai_response
                }
            }
            
        except Exception as e:
            print(f"Error creating flowchart structure: {e}")
            return self._create_basic_flowchart(goal, horizon, risk)
    
    def _parse_steps_from_response(self, response: str) -> List[Dict]:
        """Parse steps from OpenAI response"""
        steps = []
        
        # Basic parsing - looking for numbered items or bullet points
        lines = response.split('\n')
        current_step = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for numbered steps or bullet points
            if (line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) or
                line.startswith(('•', '-', '*')) or
                'step' in line.lower()):
                
                if current_step:
                    steps.append(current_step)
                
                current_step = {
                    "title": line[:50] + "..." if len(line) > 50 else line,
                    "description": line
                }
            elif current_step and len(line) > 10:
                # Add to current step description
                current_step["description"] += " " + line
        
        if current_step:
            steps.append(current_step)
        
        # If no steps found, create generic ones
        if not steps:
            steps = [
                {"title": "Assess Current Financial Status", "description": "Evaluate current income, expenses, and assets"},
                {"title": "Set Specific Targets", "description": f"Define specific milestones for {response[:100]}"},
                {"title": "Create Investment Strategy", "description": "Develop investment approach based on risk tolerance"},
                {"title": "Monitor and Adjust", "description": "Regular review and adjustment of the plan"}
            ]
        
        return steps[:6]  # Limit to 6 steps for better visualization
    
    def _parse_enhanced_steps_from_response(self, response: str, horizon: str, risk: str) -> List[Dict]:
        """Parse enhanced steps from OpenAI response with additional metadata"""
        steps = []
        
        # Enhanced parsing with more intelligence
        lines = response.split('\n')
        current_step = None
        
        step_keywords = ['step', 'phase', 'stage', 'milestone', 'action', 'goal']
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for numbered steps, bullet points, or step keywords
            if (line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) or
                line.startswith(('•', '-', '*', '→', '▶')) or
                any(keyword in line.lower() for keyword in step_keywords)):
                
                if current_step:
                    steps.append(current_step)
                
                # Extract timeline and metrics if mentioned
                timeline = self._extract_timeline(line, horizon)
                metrics = self._extract_metrics(line)
                priority = self._extract_priority(line, risk)
                
                current_step = {
                    "title": self._clean_title(line),
                    "description": line,
                    "timeline": timeline,
                    "metrics": metrics,
                    "priority": priority,
                    "icon": self._suggest_icon(line)
                }
            elif current_step and len(line) > 10:
                # Add to current step description
                current_step["description"] += " " + line
                # Update metrics and timeline if found in additional text
                if not current_step.get("timeline"):
                    current_step["timeline"] = self._extract_timeline(line, horizon)
                if not current_step.get("metrics"):
                    current_step["metrics"] = self._extract_metrics(line)
        
        if current_step:
            steps.append(current_step)
        
        # If no steps found, create enhanced generic ones
        if not steps:
            steps = self._create_default_enhanced_steps(horizon, risk)
        
        return steps[:8]  # Limit to 8 steps for optimal visualization
    
    def _clean_title(self, text: str) -> str:
        """Clean and shorten title"""
        # Remove numbering and bullet points
        text = text.lstrip('0123456789.-•*→▶ ')
        # Limit to 4 words or 30 characters
        words = text.split()[:4]
        title = ' '.join(words)
        return title[:30] + "..." if len(title) > 30 else title
    
    def _extract_timeline(self, text: str, horizon: str) -> str:
        """Extract timeline information from text"""
        time_indicators = ['week', 'month', 'quarter', 'year', 'day']
        for indicator in time_indicators:
            if indicator in text.lower():
                return f"Target: {horizon.split()[0]} {indicator}s"
        return f"Within {horizon}"
    
    def _extract_metrics(self, text: str) -> str:
        """Extract success metrics from text"""
        if any(word in text.lower() for word in ['save', 'dollar', '$', 'percent', '%']):
            return "Measurable targets defined"
        if any(word in text.lower() for word in ['complete', 'achieve', 'reach']):
            return "Completion-based"
        return "Progress trackable"
    
    def _extract_priority(self, text: str, risk: str) -> str:
        """Determine priority based on content and risk tolerance"""
        high_priority_words = ['emergency', 'debt', 'critical', 'urgent', 'foundation']
        if any(word in text.lower() for word in high_priority_words):
            return "high"
        return "normal"
    
    def _suggest_icon(self, text: str) -> str:
        """Suggest appropriate icon based on step content"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['assess', 'evaluate', 'analyze']):
            return "ChartBarIcon"
        elif any(word in text_lower for word in ['save', 'budget', 'money']):
            return "BanknotesIcon"
        elif any(word in text_lower for word in ['invest', 'portfolio']):
            return "TrendingUpIcon"
        elif any(word in text_lower for word in ['monitor', 'track', 'review']):
            return "ClockIcon"
        elif any(word in text_lower for word in ['plan', 'strategy']):
            return "DocumentTextIcon"
        return "CogIcon"
    
    def _calculate_enhanced_positions(self, step_count: int) -> List[Dict]:
        """Calculate optimal positions for nodes with no overlapping"""
        positions = []
        
        if step_count <= 3:
            # Vertical linear layout for small counts
            for i in range(step_count):
                positions.append({"x": 400, "y": 200 + i * 200})
        elif step_count <= 6:
            # Staggered layout for medium counts
            for i in range(step_count):
                if i % 2 == 0:
                    x = 300  # Left side
                else:
                    x = 500  # Right side
                y = 200 + (i // 2) * 250
                positions.append({"x": x, "y": y})
        else:
            # Grid layout for larger counts with proper spacing
            cols = min(3, step_count)  # Max 3 columns
            rows = (step_count + cols - 1) // cols
            
            # Calculate spacing to prevent overlaps
            node_width = 220  # Approximate node width
            node_height = 120  # Approximate node height
            spacing_x = max(300, node_width + 80)  # Minimum 80px gap
            spacing_y = max(200, node_height + 80)  # Minimum 80px gap
            
            # Center the grid
            start_x = 200 if cols == 1 else 100 if cols == 2 else 50
            start_y = 200
            
            for i in range(step_count):
                row = i // cols
                col = i % cols
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                positions.append({"x": x, "y": y})
        
        return positions
    
    def _determine_node_type(self, step: Dict, index: int, total: int) -> str:
        """Determine the appropriate node type based on step content"""
        text = step.get("description", "").lower()
        
        if any(word in text for word in ['decide', 'choose', 'evaluate', 'assess']):
            return "decisionNode"
        elif index == total - 1:  # Last step before end
            return "processNode"
        else:
            return "processNode"
    
    def _get_edge_style(self, priority: str) -> Dict:
        """Get edge styling based on priority"""
        if priority == "high":
            return {
                "stroke": "#ef4444",
                "strokeWidth": 4,
                "filter": "drop-shadow(0 2px 4px rgba(239, 68, 68, 0.4))"
            }
        else:
            return {
                "stroke": "#3b82f6",
                "strokeWidth": 3,
                "filter": "drop-shadow(0 2px 4px rgba(59, 130, 246, 0.3))"
            }
    
    def _add_feedback_loops(self, nodes: List, edges: List, steps: List):
        """Add feedback loops for monitoring and adjustment"""
        # Find monitoring/review steps
        for i, step in enumerate(steps):
            if any(word in step.get("description", "").lower() for word in ['monitor', 'review', 'adjust']):
                # Add feedback edge to earlier planning step
                planning_step = max(0, i - 2)
                edges.append({
                    "id": f"feedback_{i}",
                    "source": f"step_{i+1}",
                    "target": f"step_{planning_step+1}" if planning_step > 0 else "start",
                    "type": "smoothstep",
                    "animated": True,
                    "style": {
                        "stroke": "#6366f1",
                        "strokeWidth": 2,
                        "strokeDasharray": "8,4",
                        "filter": "drop-shadow(0 1px 2px rgba(99, 102, 241, 0.3))"
                    },
                    "label": "Adjust if needed"
                })
    
    def _extract_investment_allocation(self, response: str) -> Dict:
        """Extract investment allocation details from OpenAI response"""
        allocation = {}
        
        # Look for investment allocation patterns
        import re
        
        # Pattern to find ₹amount → investment type
        pattern = r'₹\s*(\d+(?:,\d+)*)\s*[→\-]\s*([^–\n]+)(?:[–\-]([^.\n]+))?'
        matches = re.findall(pattern, response)
        
        for match in matches:
            amount = match[0].replace(',', '')
            investment_type = match[1].strip()
            reasoning = match[2].strip() if len(match) > 2 else ""
            
            allocation[investment_type] = {
                "amount": f"₹{amount}",
                "reasoning": reasoning
            }
        
        return allocation
    
    def _create_default_enhanced_steps(self, horizon: str, risk: str) -> List[Dict]:
        """Create enhanced default steps when parsing fails"""
    def _create_default_enhanced_steps(self, horizon: str, risk: str) -> List[Dict]:
        """Create enhanced default steps when parsing fails"""
        return [
            {
                "title": "Goal Assessment",
                "description": "Define specific financial target and extract required investment amount",
                "timeline": "Week 1",
                "metrics": "Clear target amount identified",
                "priority": "high",
                "icon": "FlagIcon"
            },
            {
                "title": "Financial Health Check",
                "description": "Comprehensive evaluation of current income, expenses, assets, and existing investments",
                "timeline": "Week 1-2",
                "metrics": "Complete financial snapshot",
                "priority": "high",
                "icon": "ChartBarIcon"
            },
            {
                "title": "Investment Allocation",
                "description": f"Create diversified portfolio based on {risk} risk tolerance and {horizon} timeframe with specific amounts for FD, Mutual Funds, Equity, and Emergency funds",
                "timeline": "Week 3",
                "metrics": "Detailed allocation plan with exact amounts",
                "priority": "high",
                "icon": "BanknotesIcon"
            },
            {
                "title": "Account Setup",
                "description": "Open necessary investment accounts, SIP mandates, and complete KYC requirements",
                "timeline": "Week 4",
                "metrics": "All accounts operational",
                "priority": "normal",
                "icon": "DocumentTextIcon"
            },
            {
                "title": "Investment Execution",
                "description": "Execute the planned allocations - start SIPs, make lump sum investments, and set up recurring deposits",
                "timeline": "Month 2",
                "metrics": "All investments activated",
                "priority": "normal",
                "icon": "PlayIcon"
            },
            {
                "title": "Progress Monitoring",
                "description": "Monthly portfolio review, performance tracking, and rebalancing if needed",
                "timeline": "Ongoing monthly",
                "metrics": "Monthly review reports",
                "priority": "normal",
                "icon": "ClockIcon"
            }
        ]
    
    def _create_enhanced_basic_flowchart(self, goal: str, horizon: str, risk: str) -> Dict:
        """Create an enhanced basic flowchart as fallback with proper spacing and investment allocation"""
        
        # Extract amount and create basic allocation
        amount = self._extract_amount_from_goal(goal)
        basic_allocation = self._create_basic_investment_allocation(amount, horizon, risk)
        
        nodes = [
            {
                "id": "start",
                "type": "startNode",
                "position": {"x": 400, "y": 50},
                "data": {
                    "label": "Financial Goal",
                    "description": f"{goal} | Target: {amount}",
                    "icon": "RocketLaunchIcon"
                }
            },
            {
                "id": "assess",
                "type": "processNode",
                "position": {"x": 150, "y": 250},
                "data": {
                    "label": "Financial Assessment",
                    "description": "Evaluate current financial position, income, expenses, and existing investments",
                    "icon": "ChartBarIcon"
                }
            },
            {
                "id": "allocate",
                "type": "decisionNode",
                "position": {"x": 650, "y": 250},
                "data": {
                    "label": "Investment Allocation",
                    "description": f"Diversified allocation based on {risk} risk tolerance: {basic_allocation['summary']}",
                    "icon": "BanknotesIcon"
                }
            },
            {
                "id": "implement",
                "type": "processNode",
                "position": {"x": 150, "y": 500},
                "data": {
                    "label": "Execute Investments",
                    "description": "Open accounts, start SIPs, make lump sum investments as per allocation plan",
                    "icon": "PlayIcon"
                }
            },
            {
                "id": "monitor",
                "type": "processNode",
                "position": {"x": 650, "y": 500},
                "data": {
                    "label": "Track & Rebalance",
                    "description": "Monthly review, performance tracking, and portfolio rebalancing if needed",
                    "icon": "ClockIcon"
                }
            },
            {
                "id": "end",
                "type": "endNode",
                "position": {"x": 400, "y": 750},
                "data": {
                    "label": "Goal Achievement",
                    "description": f"Successfully accumulate {amount} for {goal}",
                    "icon": "TrophyIcon"
                }
            }
        ]
        
        edges = [
            {
                "id": "e1",
                "source": "start",
                "target": "assess",
                "type": "smoothstep",
                "animated": True,
                "style": {
                    "stroke": "#3b82f6",
                    "strokeWidth": 3,
                    "filter": "drop-shadow(0 2px 4px rgba(59, 130, 246, 0.3))"
                }
            },
            {
                "id": "e2",
                "source": "start",
                "target": "allocate",
                "type": "smoothstep",
                "animated": True,
                "style": {
                    "stroke": "#3b82f6",
                    "strokeWidth": 3,
                    "filter": "drop-shadow(0 2px 4px rgba(59, 130, 246, 0.3))"
                }
            },
            {
                "id": "e3",
                "source": "assess",
                "target": "implement",
                "type": "smoothstep",
                "animated": True,
                "style": {
                    "stroke": "#10b981",
                    "strokeWidth": 3,
                    "filter": "drop-shadow(0 2px 4px rgba(16, 185, 129, 0.3))"
                }
            },
            {
                "id": "e4",
                "source": "allocate",
                "target": "monitor",
                "type": "smoothstep",
                "animated": True,
                "style": {
                    "stroke": "#10b981",
                    "strokeWidth": 3,
                    "filter": "drop-shadow(0 2px 4px rgba(16, 185, 129, 0.3))"
                }
            },
            {
                "id": "e5",
                "source": "implement",
                "target": "end",
                "type": "smoothstep",
                "animated": True,
                "style": {
                    "stroke": "#8b5cf6",
                    "strokeWidth": 3,
                    "filter": "drop-shadow(0 2px 4px rgba(139, 92, 246, 0.3))"
                }
            },
            {
                "id": "e6",
                "source": "monitor",
                "target": "end",
                "type": "smoothstep",
                "animated": True,
                "style": {
                    "stroke": "#8b5cf6",
                    "strokeWidth": 3,
                    "filter": "drop-shadow(0 2px 4px rgba(139, 92, 246, 0.3))"
                }
            },
            {
                "id": "e7",
                "source": "monitor",
                "target": "allocate",
                "type": "smoothstep",
                "animated": True,
                "style": {
                    "stroke": "#6366f1",
                    "strokeWidth": 2,
                    "strokeDasharray": "8,4",
                    "filter": "drop-shadow(0 1px 2px rgba(99, 102, 241, 0.3))"
                },
                "label": "Rebalance portfolio"
            }
        ]
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "goal": goal,
                "time_horizon": horizon,
                "risk_tolerance": risk,
                "target_amount": amount,
                "generated_plan": f"Enhanced basic flowchart with investment allocation for {goal}. Recommended allocation: {basic_allocation['summary']}",
                "complexity": "basic_enhanced",
                "investment_allocation": basic_allocation['details']
            }
        }
    
    def _create_basic_investment_allocation(self, amount_str: str, horizon: str, risk: str) -> Dict:
        """Create basic investment allocation based on risk and horizon"""
        import re
        
        # Extract numeric amount
        amount_match = re.search(r'₹\s*(\d+(?:,\d+)*)', amount_str.replace(',', ''))
        if amount_match:
            amount = int(amount_match.group(1).replace(',', ''))
        else:
            amount = 50000  # Default
        
        allocation = {}
        
        # Determine allocation based on risk and horizon
        if 'short' in horizon.lower() or any(word in horizon.lower() for word in ['month', '6', '7', '8', '9', '10', '11']):
            # Short-term (less than 1 year)
            if risk.lower() == 'low':
                allocation = {
                    'Fixed Deposit': {'amount': int(amount * 0.7), 'reason': 'Guaranteed returns, capital safety'},
                    'Liquid Mutual Fund': {'amount': int(amount * 0.2), 'reason': 'Better returns than FD, high liquidity'},
                    'Emergency Buffer': {'amount': int(amount * 0.1), 'reason': 'Immediate access funds'}
                }
            else:
                allocation = {
                    'Short-term Debt Fund': {'amount': int(amount * 0.5), 'reason': 'Better returns than FD, moderate risk'},
                    'Liquid Fund': {'amount': int(amount * 0.3), 'reason': 'High liquidity, stable returns'},
                    'Ultra Short Duration Fund': {'amount': int(amount * 0.2), 'reason': 'Slightly higher returns, low risk'}
                }
        elif 'medium' in horizon.lower() or any(word in horizon.lower() for word in ['year', '2', '3']):
            # Medium-term (1-3 years)
            if risk.lower() == 'low':
                allocation = {
                    'Fixed Deposit': {'amount': int(amount * 0.4), 'reason': 'Capital protection, guaranteed returns'},
                    'Conservative Hybrid Fund': {'amount': int(amount * 0.4), 'reason': 'Balanced growth with safety'},
                    'Liquid Fund': {'amount': int(amount * 0.2), 'reason': 'Emergency liquidity'}
                }
            elif risk.lower() == 'medium':
                allocation = {
                    'Balanced Mutual Fund': {'amount': int(amount * 0.5), 'reason': 'Growth with moderate risk'},
                    'Fixed Deposit': {'amount': int(amount * 0.3), 'reason': 'Stability component'},
                    'Liquid Fund': {'amount': int(amount * 0.2), 'reason': 'Liquidity buffer'}
                }
            else:  # High risk
                allocation = {
                    'Equity Mutual Fund': {'amount': int(amount * 0.6), 'reason': 'High growth potential'},
                    'Debt Fund': {'amount': int(amount * 0.3), 'reason': 'Risk mitigation'},
                    'Emergency Fund': {'amount': int(amount * 0.1), 'reason': 'Safety net'}
                }
        else:
            # Long-term (3+ years)
            if risk.lower() == 'low':
                allocation = {
                    'Conservative Hybrid Fund': {'amount': int(amount * 0.5), 'reason': 'Steady growth with safety'},
                    'PPF/ELSS': {'amount': int(amount * 0.3), 'reason': 'Tax benefits, long-term growth'},
                    'Fixed Deposit': {'amount': int(amount * 0.2), 'reason': 'Capital protection'}
                }
            elif risk.lower() == 'medium':
                allocation = {
                    'Large Cap Equity Fund': {'amount': int(amount * 0.4), 'reason': 'Stable equity growth'},
                    'Balanced Fund': {'amount': int(amount * 0.4), 'reason': 'Diversified exposure'},
                    'Debt Fund': {'amount': int(amount * 0.2), 'reason': 'Risk reduction'}
                }
            else:  # High risk
                allocation = {
                    'Mid/Small Cap Fund': {'amount': int(amount * 0.4), 'reason': 'High growth potential'},
                    'Large Cap Fund': {'amount': int(amount * 0.3), 'reason': 'Stable equity base'},
                    'ELSS': {'amount': int(amount * 0.2), 'reason': 'Tax saving with growth'},
                    'Emergency Fund': {'amount': int(amount * 0.1), 'reason': 'Liquidity safety'}
                }
        
        # Format allocation for display
        formatted_allocation = {}
        summary_parts = []
        
        for investment_type, details in allocation.items():
            formatted_amount = f"₹{details['amount']:,}"
            formatted_allocation[investment_type] = {
                'amount': formatted_amount,
                'reasoning': details['reason']
            }
            summary_parts.append(f"{formatted_amount} in {investment_type}")
        
        return {
            'details': formatted_allocation,
            'summary': ' | '.join(summary_parts)
        }
