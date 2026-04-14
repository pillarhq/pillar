---
draft: true
title: "Routing software"
subtitle: "MCP servers and API keys make a new kind of product possible."
date: "2026-04-07"
author: "JJ Maxwell"
slug: "beyond-saas-routing-software"
description: "MCP servers and API keys make a new kind of product possible — one that routes work across many tools from a single interface."
---

Most of the conversation about MCP servers has been about connecting AI models to tools. That's useful. But the more interesting part is one level up.

If you have MCP servers that wrap different services, and API keys that authenticate into them, you have the pieces for something new: a product that routes work across many systems from one interface.

Think OpenRouter, but for work instead of model calls.

## The OpenRouter parallel

OpenRouter solved a real problem. You want access to many LLMs. You don't want to manage separate keys, rate limits, and provider quirks for each one. OpenRouter gives you one endpoint and routes your request to the right model.

Now take that up a level. Instead of routing a prompt to a model, route a job across a dozen tools. Pull data from the CRM. Enrich it with external sources. Draft outreach. Send it through the sequencing tool. Read back reply patterns. Connect that to analytics. Connect analytics to billing. Figure out what actually worked.

Today, a person holds that whole chain together manually. Or a team writes custom integrations. Or someone builds a stack of Zapier automations that one person sort of understands. MCP servers change this. Each server wraps a tool behind a standard interface. A product on top can route work between them without custom integrations for every combination.

The user brings the API keys. The product brings the routing.

## Fifteen tools, one job

Cody Schneider posted a tweet showing the workflow for making UGC ads for SaaS. Scrape Reddit for pain points. Have Claude write scripts. Send them to HeyGen. Clean up the output with `ffmpeg`. Add captions. Publish to Facebook. Pull in Facebook data, Google Analytics, PostHog, and Stripe. Figure out which ads lead to actual customer value. Remix the winners. Build landing pages. Repeat. ([link](https://x.com/codyschneider/status/2041274794394431524))

That is maybe fifteen tools. Every one of those steps could be behind an MCP server. The work of deciding what goes where, in what order, with what data — that is routing.

Read that list once and it sounds like a pile of disconnected tasks. Read it again and it looks like a product.

## Why this is newly possible

Two things had to exist for this product type to work.

First, a standard interface for tools. Before MCP, every integration was custom. If you wanted your product to talk to HubSpot and Salesforce and a homegrown CRM, you built three separate integrations. MCP servers give each tool the same interface, so a product on top can talk to any of them the same way.

Second, AI models that can reason about tool selection. The routing layer needs to decide: given this job, which tool do I call next, with what inputs, and what do I do with the output? That's judgment, not API mapping. Language models can do this now.

Those two things together create a product type that didn't exist before. A SaaS tool gives you one capability with a fixed workflow. Zapier lets you wire connections one at a time. This is different: a layer that sits across many tools and uses AI to decide which one to call next.

## The user builds the stack

No single company can build integrations for every tool a team uses. The combinations are too many, and every team's stack is different. In traditional software, the product builder decides which integrations exist. If your tool isn't on the list, you wait.

With MCP servers, the end user adds a tool by plugging in an API key. That key connects to an MCP server. The server exposes tool calls. The routing layer picks them up. The user didn't write code. They didn't file a feature request. They just added a key.

The product gets more useful as the user connects more tools, without the product team shipping anything.

## What's still hard

MCP servers handle the connection layer. The product layer on top is harder.

If you hold API keys to someone's CRM, ad platform, and billing system, you need real access controls. A job that crosses ten tools over three days needs to remember where it is, what it tried, and what failed. And people will only hand over keys to sensitive systems if they trust the product to use them carefully.

## The moat is in the routing

Everyone right now is fighting to be the interface. The chat. The dashboard. The copilot. Most will lose because they only connect to a few things.

A product that only connects to three tools is a feature. A product that connects to whatever the user plugs in, routes work across all of it, and keeps the loop running — that is a different category. The more tools the user connects, the harder it is to leave.
