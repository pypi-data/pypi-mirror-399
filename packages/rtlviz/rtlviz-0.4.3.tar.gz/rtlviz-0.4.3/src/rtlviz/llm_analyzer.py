#!/usr/bin/env python3
"""
LLM Analyzer Module - Generic for ANY Verilog IP

Uses MCP Sampling to request LLM completions from the client (agent).
No API key required - leverages the client's LLM capabilities.

Works for: CPUs, Controllers, Switches, SoCs, FPGAs, anything!
"""

import json
import re
import sys
from typing import Dict, List, Optional, Tuple, Any

from mcp.server import Server
from mcp.types import (
    SamplingMessage,
    TextContent as SamplingTextContent,
    CreateMessageRequestParams,
    CreateMessageResult,
)

from .rtl_parser import ModuleInstance

# Prompt version for traceability and debugging reproducibility issues
PROMPT_VERSION = "2.0.0"

# Vibrant color palette for functional groups
GROUP_COLORS = [
    ('#E3F2FD', '#1565C0'),  # Blue (IF)
    ('#E8F5E9', '#2E7D32'),  # Green (ID)
    ('#FFF3E0', '#EF6C00'),  # Orange (EX)
    ('#FCE4EC', '#C2185B'),  # Pink (MEM)
    ('#F3E5F5', '#7B1FA2'),  # Purple (WB)
    ('#E0F7FA', '#00838F'),  # Cyan
    ('#FFF8E1', '#FF8F00'),  # Amber
    ('#FFEBEE', '#C62828'),  # Red
    ('#E8EAF6', '#5C6BC0'),  # Indigo (Latches)
    ('#F1F8E9', '#558B2F'),  # Light Green
]

# CPU Pipeline stage specific colors
CPU_STAGE_COLORS = {
    'IF': ('#E3F2FD', '#1976D2'),
    'IF_ID': ('#E8EAF6', '#5C6BC0'),
    'ID': ('#E8F5E9', '#388E3C'),
    'ID_EX': ('#E8EAF6', '#5C6BC0'),
    'EX': ('#FFF3E0', '#F57C00'),
    'EX_MEM': ('#E8EAF6', '#5C6BC0'),
    'MEM': ('#FCE4EC', '#C2185B'),
    'MEM_WB': ('#E8EAF6', '#5C6BC0'),
    'WB': ('#F3E5F5', '#7B1FA2'),
}


async def request_sampling(server: Server, prompt: str, max_tokens: int = 800) -> Optional[str]:
    """
    Request LLM completion from the MCP client via sampling.
    
    Args:
        server: The MCP Server instance
        prompt: The prompt to send
        max_tokens: Maximum tokens for response
        
    Returns:
        The LLM response text, or None if sampling fails
    """
    try:
        # Create the sampling request
        result: CreateMessageResult = await server.request_context.session.create_message(
            messages=[
                SamplingMessage(
                    role="user",
                    content=SamplingTextContent(type="text", text=prompt)
                )
            ],
            max_tokens=max_tokens,
        )
        
        # Extract text from response
        if result and result.content:
            if hasattr(result.content, 'text'):
                return result.content.text
            elif isinstance(result.content, dict) and 'text' in result.content:
                return result.content['text']
        
        return None
        
    except Exception as e:
        print(f"MCP Sampling failed: {e}", file=sys.stderr)
        return None


async def analyze_design(server: Server, top_module_code: str, instance_list: List[str]) -> Dict:
    """
    Holistic analysis of entire design using MCP Sampling.
    
    Args:
        server: The MCP Server instance
        top_module_code: Source code of top module (first 3000 chars)
        instance_list: List of instance names and types
        
    Returns:
        Dict with: design_type, functional_groups (with assigned instances)
    """
    # Build instance summary
    instances_text = "\n".join(instance_list[:30])  # Limit to 30 for token efficiency
    
    prompt = f"""You are an RTL design analyzer. Classify Verilog module instances into functional groups.

## INPUT
TOP MODULE CODE:
```verilog
{top_module_code[:3000]}
```

INSTANCES TO CLASSIFY:
{instances_text}

## OUTPUT REQUIREMENTS

You MUST return ONLY a JSON object between BEGIN_JSON and END_JSON markers.
Do NOT include any explanation, markdown, or other text outside the markers.

### For CPU/Processor Designs (set is_cpu: true)
Use EXACTLY these pipeline stage names (no variations allowed):
- "IF": Instruction Fetch (PC, Instruction Memory, PC adders)
- "IF_ID": IF/ID Pipeline Register ONLY
- "ID": Instruction Decode (Control, Registers, Sign Extend, Hazard Detection)
- "ID_EX": ID/EX Pipeline Register ONLY
- "EX": Execute (ALU, ALU Control, MUXes, Forwarding)
- "EX_MEM": EX/MEM Pipeline Register ONLY
- "MEM": Memory Access (Data Memory ONLY)
- "MEM_WB": MEM/WB Pipeline Register ONLY
- "WB": Write Back (MemToReg MUX)

### For Non-CPU Designs (set is_cpu: false)
Use functional groups like: "Host_Interface", "TX_Path", "RX_Path", "Control", "Datapath", "Memory", "PHY_Interface", "Buffer", "Parser"

## STRICT RULES
1. EVERY instance MUST be assigned to exactly ONE group - no orphans allowed
2. Group names MUST be 1-3 words, use underscores not spaces
3. is_cpu MUST be boolean (true or false)
4. design_type MUST be a short phrase (max 6 words)
5. Match instance names exactly as provided in the input list

## OUTPUT FORMAT
BEGIN_JSON
{{
    "design_type": "<short description, e.g. '5-Stage RISC-V CPU' or 'Ethernet MAC Controller'>",
    "is_cpu": <true|false>,
    "groups": [
        {{"name": "<GroupName>", "instances": ["exact_inst_name1", "exact_inst_name2"]}},
        ...
    ]
}}
END_JSON"""

    result_text = await request_sampling(server, prompt, max_tokens=800)
    
    if result_text:
        try:
            # Extract JSON - prefer BEGIN_JSON/END_JSON markers for stricter parsing
            json_text = None
            marker_match = re.search(r'BEGIN_JSON\s*([\s\S]*?)\s*END_JSON', result_text)
            if marker_match:
                json_text = marker_match.group(1).strip()
            else:
                # Fallback to generic JSON extraction
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group()
            
            if json_text:
                result = json.loads(json_text)
                is_cpu = result.get("is_cpu", False)
                
                # Assign colors to groups
                for i, group in enumerate(result.get("groups", [])):
                    group_name = group.get("name", "")
                    
                    # Use CPU stage colors if applicable
                    if is_cpu and group_name in CPU_STAGE_COLORS:
                        fill, border = CPU_STAGE_COLORS[group_name]
                    else:
                        color_idx = i % len(GROUP_COLORS)
                        fill, border = GROUP_COLORS[color_idx]
                    
                    group["fill_color"] = fill
                    group["border_color"] = border
                return result
        except json.JSONDecodeError:
            pass
    
    return _fallback_design_analysis(instance_list)


def _fallback_design_analysis(instance_list: List[str]) -> Dict:
    """Fallback when sampling not available - simple pattern grouping."""
    groups = {}
    
    for item in instance_list:
        parts = item.split(" : ")
        inst_name = parts[0] if parts else item
        
        # Simple pattern-based grouping
        name_lower = inst_name.lower()
        if any(x in name_lower for x in ['mux', 'select']):
            group = 'Multiplexers'
        elif any(x in name_lower for x in ['reg', 'latch', 'ff']):
            group = 'Registers'
        elif any(x in name_lower for x in ['mem', 'ram', 'rom', 'fifo']):
            group = 'Memory'
        elif any(x in name_lower for x in ['ctrl', 'control', 'fsm', 'state']):
            group = 'Control'
        elif any(x in name_lower for x in ['alu', 'add', 'mult', 'div']):
            group = 'Datapath'
        else:
            group = 'Logic'
        
        if group not in groups:
            groups[group] = []
        groups[group].append(inst_name)
    
    # Convert to expected format
    result_groups = []
    for i, (name, instances) in enumerate(groups.items()):
        color_idx = i % len(GROUP_COLORS)
        result_groups.append({
            "name": name,
            "instances": instances,
            "fill_color": GROUP_COLORS[color_idx][0],
            "border_color": GROUP_COLORS[color_idx][1]
        })
    
    return {
        "design_type": "RTL Design",
        "groups": result_groups
    }


async def classify_instance_with_context(
    server: Server,
    instance: ModuleInstance,
    module_code: str,
    design_context: str
) -> Dict:
    """
    Classify a single instance with design context using MCP Sampling.
    
    Args:
        server: The MCP Server instance
        instance: The module instance
        module_code: Source code of the module (first 1000 chars)
        design_context: What type of design this is
        
    Returns:
        Dict with semantic_type, description
    """
    prompt = f"""Classify this Verilog module instance for a block diagram.

DESIGN: {design_context}
MODULE TYPE: {instance.module_type}
INSTANCE NAME: {instance.instance_name}

## SEMANTIC TYPE DEFINITIONS (choose exactly ONE):
- "alu": Arithmetic Logic Unit (performs +, -, *, /, AND, OR, XOR, shifts)
- "mux": Multiplexer (selects 1 of N inputs via select signal)
- "memory": RAM, ROM, Data Memory, Instruction Memory (has address/data ports)
- "register": Register file or single register (stores values, read/write enable)
- "pipeline_reg": Pipeline stage register (IF_ID, ID_EX, EX_MEM, MEM_WB ONLY)
- "control": Control unit, FSM, decoder (generates control signals)
- "compare": Comparator, equality check, hazard detection, forwarding unit
- "adder": Simple adder (PC+4, branch offset adder)
- "transform": Sign extend, shift, zero extend, data width conversion
- "logic": Generic logic (use ONLY if no other type matches)

## PATTERN MATCHING RULES:
- Name contains "MUX" or "mux" or "Select" or "Sel" → mux
- Name contains "ALU" (case-insensitive) → alu
- Name contains "Mem" or "RAM" or "ROM" or "Memory" → memory
- Name contains "Reg" or "Register" (but NOT IF_ID, ID_EX, etc.) → register
- Name matches "IF_ID" or "ID_EX" or "EX_MEM" or "MEM_WB" → pipeline_reg
- Name contains "Ctrl" or "Control" or "FSM" or "Decode" → control
- Name contains "Hazard" or "Forward" or "Compare" → compare
- Name contains "Add" or "Adder" (simple addition) → adder
- Name contains "Extend" or "Shift" or "Sign" → transform

## OUTPUT FORMAT
Return ONLY this JSON object (no explanation, no markdown):
{{"semantic_type": "<type>", "description": "<Short Label>"}}"""

    result_text = await request_sampling(server, prompt, max_tokens=80)
    
    if result_text:
        try:
            json_match = re.search(r'\{[^{}]+\}', result_text)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    return _simple_classify(instance)


def _simple_classify(instance: ModuleInstance) -> Dict:
    """Simple classification based on name."""
    name = instance.module_type.lower()
    
    if 'mux' in name:
        return {"semantic_type": "mux", "description": "Multiplexer"}
    elif any(x in name for x in ['mem', 'ram', 'rom']):
        return {"semantic_type": "memory", "description": "Memory"}
    elif any(x in name for x in ['reg', 'latch']):
        return {"semantic_type": "register", "description": "Register"}
    elif any(x in name for x in ['alu', 'add']):
        return {"semantic_type": "datapath", "description": "ALU"}
    elif 'ctrl' in name or 'control' in name:
        return {"semantic_type": "control", "description": "Controller"}
    else:
        return {"semantic_type": "logic", "description": instance.module_type}


async def enhance_instances_holistic(
    server: Server,
    instances: list,
    modules: Dict,
    top_module_code: str = "",
    use_llm: bool = True
) -> Tuple[Dict, str]:
    """
    Enhanced instance analysis with holistic design understanding.
    
    Args:
        server: The MCP Server instance
        instances: List of ModuleInstance objects
        modules: Dict of parsed modules
        top_module_code: Source code of top module
        use_llm: Whether to use LLM (via sampling)
        
    Returns:
        Tuple of (group_assignments dict, design_type string)
    """
    # Build instance list for analysis
    instance_list = [f"{inst.instance_name} : {inst.module_type}" for inst in instances]
    
    # Step 1: Analyze entire design holistically
    if use_llm:
        design_analysis = await analyze_design(server, top_module_code, instance_list)
    else:
        design_analysis = _fallback_design_analysis(instance_list)
    
    design_type = design_analysis.get("design_type", "RTL Design")
    groups = design_analysis.get("groups", [])
    
    # Build instance->group mapping
    instance_to_group = {}
    for group in groups:
        group_name = group.get("name", "Logic")
        for inst_name in group.get("instances", []):
            # Handle both "inst_name" and "inst_name : type" formats
            clean_name = inst_name.split(" : ")[0].strip()
            instance_to_group[clean_name] = {
                "group": group_name,
                "fill_color": group.get("fill_color", "#ECEFF1"),
                "border_color": group.get("border_color", "#607D8B")
            }
    
    # Step 2: Enhance each instance
    for inst in instances:
        # Get group assignment
        group_info = instance_to_group.get(inst.instance_name, {
            "group": "Logic",
            "fill_color": "#F5F5F5",
            "border_color": "#424242"
        })
        
        inst.pipeline_stage = group_info["group"]
        inst.cluster_fill_color = group_info["fill_color"]
        inst.cluster_border_color = group_info["border_color"]
        
        # Don't set inst.fill_color - let dot_generator use component style defaults
        # unless specifically needed for generic logic blocks.
        if inst.semantic_type == 'logic' and not use_llm:
             inst.fill_color = group_info["fill_color"]
        
        # Get module code for detailed classification
        module_info = modules.get(inst.module_type)
        module_code = ""
        if module_info and hasattr(module_info, 'raw_code'):
            module_code = module_info.raw_code
        
        # Classify instance
        if use_llm:
            classification = await classify_instance_with_context(server, inst, module_code, design_type)
        else:
            classification = _simple_classify(inst)
        
        inst.semantic_type = classification.get("semantic_type", "logic")
        inst.description = classification.get("description", inst.module_type)
    
    return instance_to_group, design_type


# Keep old function for backward compatibility (now async)
async def enhance_instances(
    server: Server,
    instances: list,
    modules: Dict,
    use_llm: bool = True
) -> None:
    """Legacy function - wraps new holistic approach."""
    # Get top module code if available
    top_code = ""
    for mod in modules.values():
        if hasattr(mod, 'raw_code'):
            top_code = mod.raw_code
            break
    
    await enhance_instances_holistic(server, instances, modules, top_code, use_llm)
