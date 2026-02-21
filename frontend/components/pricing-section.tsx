import { Check } from "lucide-react";

const plans = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Perfect for occasional use",
    features: [
      "10 PDF conversions/month",
      "5 AI questions/month",
      "Basic PDF tools",
      "100MB max file size",
      "Community support"
    ],
    buttonText: "Get Started",
    buttonVariant: "outline",
    popular: false
  },
  {
    name: "Pro",
    price: "$29",
    period: "per month",
    description: "For professionals and small teams",
    features: [
      "100 PDF conversions/month",
      "50 AI questions/month",
      "All PDF tools",
      "500MB max file size",
      "API access",
      "Priority support",
      "No watermarks"
    ],
    buttonText: "Start Free Trial",
    buttonVariant: "primary",
    popular: true
  },
  {
    name: "Business",
    price: "$99",
    period: "per month",
    description: "For growing businesses",
    features: [
      "500 PDF conversions/month",
      "250 AI questions/month",
      "Team collaboration",
      "1GB max file size",
      "Advanced API",
      "White-label option",
      "Dedicated support",
      "Custom workflows"
    ],
    buttonText: "Contact Sales",
    buttonVariant: "outline",
    popular: false
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "tailored",
    description: "For large organizations",
    features: [
      "Unlimited conversions",
      "Unlimited AI questions",
      "Custom integrations",
      "On-premise deployment",
      "SLA guarantee",
      "Custom AI training",
      "24/7 phone support",
      "Account manager"
    ],
    buttonText: "Schedule Demo",
    buttonVariant: "outline",
    popular: false
  }
];

export function PricingSection() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
      {plans.map((plan, index) => (
        <div
          key={index}
          className={`
            relative rounded-2xl border p-8
            ${plan.popular 
              ? "border-blue-500 shadow-xl bg-gradient-to-b from-blue-50 to-white" 
              : "border-gray-200 bg-white"
            }
          `}
        >
          {plan.popular && (
            <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
              <span className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                Most Popular
              </span>
            </div>
          )}
          
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              {plan.name}
            </h3>
            <div className="flex items-baseline justify-center mb-2">
              <span className="text-4xl font-bold text-gray-900">
                {plan.price}
              </span>
              {plan.price !== "Custom" && (
                <span className="text-gray-600 ml-2">/month</span>
              )}
            </div>
            <p className="text-gray-600">{plan.description}</p>
          </div>
          
          <div className="mb-8">
            <ul className="space-y-4">
              {plan.features.map((feature, featureIndex) => (
                <li key={featureIndex} className="flex items-start">
                  <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">{feature}</span>
                </li>
              ))}
            </ul>
          </div>
          
          <button
            className={`
              w-full py-3 rounded-full font-semibold transition-colors
              ${plan.buttonVariant === "primary" 
                ? "bg-blue-600 text-white hover:bg-blue-700" 
                : "border border-gray-300 text-gray-700 hover:bg-gray-50"
              }
            `}
          >
            {plan.buttonText}
          </button>
          
          {plan.name === "Free" && (
            <p className="text-center text-sm text-gray-500 mt-4">
              No credit card required
            </p>
          )}
          
          {plan.name === "Pro" && (
            <p className="text-center text-sm text-gray-500 mt-4">
              14-day free trial • Cancel anytime
            </p>
          )}
        </div>
      ))}
    </div>
  );
}